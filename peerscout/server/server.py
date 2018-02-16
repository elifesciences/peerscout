import os
import datetime
import logging

from flask import Flask, request, send_from_directory, jsonify, url_for
from flask.json import JSONEncoder
from flask_cors import CORS
from joblib import Memory

from .services import (
  ManuscriptModel,
  load_similarity_model_from_database,
  RecommendReviewers
)

from .auth.FlaskAuth0 import (
  FlaskAuth0,
  parse_allowed_ips,
  get_remote_ip
)

from .auth.EmailValidator import (
  EmailValidator,
  parse_valid_domains,
  read_valid_emails
)

from ..shared.database import connect_configured_database
from ..shared.app_config import get_app_config
from ..shared.logging_config import configure_logging


NAME = 'server'

CLIENT_FOLDER = os.path.abspath('client/dist')

config = get_app_config()

data_dir = os.path.abspath(config.get('data', 'data_root', fallback='.data'))
cache_dir = os.path.join(data_dir, 'server-cache')

port = config.get('server', 'port', fallback=8080)
host = config.get('server', 'host', fallback=None)

def parse_list(s, sep=','):
  s = s.strip()
  if len(s) == 0:
    return []
  return [item.strip() for item in s.split(sep)]

valid_decisions = parse_list(config.get(
  'model', 'valid_decisions', fallback=''))
valid_manuscript_types = parse_list(config.get(
  'model', 'valid_manuscript_types', fallback=''))
published_decisions = parse_list(config.get(
  'model', 'published_decisions', fallback=''))
published_manuscript_types = parse_list(config.get(
  'model', 'published_manuscript_types', fallback=''))
filter_by_subject_area_enabled = config.getboolean(
  'model', 'filter_by_subject_area_enabled', fallback=False
)
filter_by_role = config.get(
  'model', 'filter_by_role', fallback=None
)
client_config = dict(config['client']) if 'client' in config else {}

auth0_domain = client_config.get('auth0_domain', '')

valid_emails_filename = config.get('auth', 'valid_emails', fallback=None)
valid_email_domains = parse_valid_domains(config.get('auth', 'valid_email_domains', fallback=''))
allowed_ips = parse_allowed_ips(config.get('auth', 'allowed_ips', fallback='127.0.0.1'))

configure_logging('server')

logging.getLogger('summa.preprocessing.cleaner').setLevel(logging.WARNING)

logger = logging.getLogger(NAME)

logger.debug('client dir: %s', CLIENT_FOLDER)

memory = Memory(cachedir=cache_dir, verbose=0)
logger.debug("cache directory: %s", cache_dir)
memory.clear(warn=False)

db = connect_configured_database(autocommit=True)

def load_recommender():
  with db.session.begin():
    manuscript_model = ManuscriptModel(
      db,
      valid_decisions=valid_decisions,
      valid_manuscript_types=valid_manuscript_types,
      published_decisions=published_decisions,
      published_manuscript_types=published_manuscript_types
    )
    similarity_model = load_similarity_model_from_database(
      db, manuscript_model=manuscript_model
    )
    return RecommendReviewers(
      db, manuscript_model=manuscript_model, similarity_model=similarity_model,
      filter_by_subject_area_enabled=filter_by_subject_area_enabled
    )

recommend_reviewers = load_recommender()

class CustomJSONEncoder(JSONEncoder):
  def default(self, obj): # pylint: disable=E0202
    try:
      if isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date):
        return obj.isoformat()
    except TypeError:
      pass
    return JSONEncoder.default(self, obj)

app = Flask(__name__, static_folder=CLIENT_FOLDER)
app.json_encoder = CustomJSONEncoder
CORS(app)

if auth0_domain:
  logging.info('using Auth0 domain %s', auth0_domain)
  logger.info('allowed_ips: %s', allowed_ips)
  flask_auth0 = FlaskAuth0(domain=auth0_domain, allowed_ips=allowed_ips)
  wrap_with_auth = flask_auth0.wrap_request_handler
else:
  logging.info('not enabling authentication, no Auth0 domain configured')
  flask_auth0 = None
  wrap_with_auth = lambda f: f

def update_auth():
  if flask_auth0:
    if valid_emails_filename or valid_email_domains:
      try:
        valid_emails = read_valid_emails(valid_emails_filename) if valid_emails_filename else set()
      except Exception as e:
        logger.warning('failed to load emails from %s (%s)', valid_emails_filename, e)
        valid_emails = set()
      logger.info('valid_emails: %d', len(valid_emails))
      logger.info('valid_email_domains: %s', valid_email_domains)
      flask_auth0.auth0.is_valid_email = EmailValidator(
        valid_emails=valid_emails,
        valid_email_domains=valid_email_domains
      )

update_auth()

@app.route("/api/")
def api_root():
  return jsonify({
    'links': {
      'recommend-reviewers': url_for('recommend_reviewers_api'),
      'subject-areas': url_for('subject_areas_api'),
      'keywords': url_for('keywords_api'),
      'config': url_for('config_api'),
      'run': url_for('run')
    }
  })

@memory.cache
def recommend_reviewers_as_json(manuscript_no, subject_area, keywords, abstract, role, limit):
  with db.session.begin():
    return jsonify(recommend_reviewers.recommend(
      manuscript_no,
      subject_area,
      keywords,
      abstract,
      role=role,
      limit=limit
    ))

@app.route("/api/recommend-reviewers")
@wrap_with_auth
def recommend_reviewers_api():
  manuscript_no = request.args.get('manuscript_no')
  subject_area = request.args.get('subject_area')
  keywords = request.args.get('keywords')
  abstract = request.args.get('abstract')
  limit = request.args.get('limit')
  if limit is None:
    limit = 100
  else:
    limit = int(limit)
  if keywords is None:
    return 'keywords parameter required', 400
  return recommend_reviewers_as_json(
    manuscript_no,
    subject_area,
    keywords,
    abstract,
    role=filter_by_role,
    limit=limit
  )

@app.route("/api/subject-areas")
def subject_areas_api():
  with db.session.begin():
    return jsonify(list(recommend_reviewers.get_all_subject_areas()))

@app.route("/api/keywords")
def keywords_api():
  with db.session.begin():
    return jsonify(list(recommend_reviewers.get_all_keywords()))

@app.route("/api/config")
def config_api():
  return jsonify(client_config)

@app.route("/control/reload", methods=['POST'])
def control_reload():
  global recommend_reviewers
  remote_ip = get_remote_ip()
  if remote_ip != '127.0.0.1':
    return jsonify({'ip': remote_ip}), 403
  logger.info("reloading...")
  recommend_reviewers = load_recommender()
  recommend_reviewers_as_json.clear()
  update_auth()
  return jsonify({'status': 'OK'})

@app.route('/')
def send_index():
  return app.send_static_file('index.html')

@app.route('/<path:path>')
def send_client_files(path):
  return send_from_directory(CLIENT_FOLDER, path)

def main():
  app.run(port=port, host=host, threaded=True)

if __name__ == "__main__":
  main()
