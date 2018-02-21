import os
import datetime
import logging

from flask import Blueprint, request, jsonify, url_for, Response
from flask.json import JSONEncoder
from flask_cors import CORS
from joblib import Memory

from ..services import (
  ManuscriptModel,
  load_similarity_model_from_database,
  RecommendReviewers
)

from ..auth.FlaskAuth0 import (
  FlaskAuth0,
  parse_allowed_ips,
  get_remote_ip
)

from ..auth.EmailValidator import (
  EmailValidator,
  parse_valid_domains,
  read_valid_emails
)

from ...shared.database import connect_configured_database
from ...shared.app_config import get_app_config
from ...shared.logging_config import configure_logging

LOGGER = logging.getLogger(__name__)

def parse_list(s, sep=','):
  s = s.strip()
  if len(s) == 0:
    return []
  return [item.strip() for item in s.split(sep)]

class ReloadableRecommendReviewers:
  def __init__(self, create_recommend_reviewer):
    self._create_recommend_reviewer = create_recommend_reviewer
    self._recommend_reviewer = create_recommend_reviewer()

  def __getattr__(self, name):
    return getattr(self._recommend_reviewer, name)

  def reload(self):
    self._recommend_reviewer = self._create_recommend_reviewer()

def get_recommend_reviewer_factory(db, config):
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
  return load_recommender

def create_api_blueprint(config):
  blueprint = Blueprint('api', __name__)

  data_dir = os.path.abspath(config.get('data', 'data_root', fallback='.data'))
  cache_dir = os.path.join(data_dir, 'server-cache')

  filter_by_role = config.get(
    'model', 'filter_by_role', fallback=None
  )
  client_config = dict(config['client']) if 'client' in config else {}

  auth0_domain = client_config.get('auth0_domain', '')

  valid_emails_filename = config.get('auth', 'valid_emails', fallback=None)
  valid_email_domains = parse_valid_domains(config.get('auth', 'valid_email_domains', fallback=''))
  allowed_ips = parse_allowed_ips(config.get('auth', 'allowed_ips', fallback='127.0.0.1'))

  memory = Memory(cachedir=cache_dir, verbose=0)
  LOGGER.debug("cache directory: %s", cache_dir)
  memory.clear(warn=False)

  db = connect_configured_database(autocommit=True)

  load_recommender = get_recommend_reviewer_factory(db, config)

  recommend_reviewers = ReloadableRecommendReviewers(load_recommender)

  if auth0_domain:
    logging.info('using Auth0 domain %s', auth0_domain)
    LOGGER.info('allowed_ips: %s', allowed_ips)
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
          LOGGER.warning('failed to load emails from %s (%s)', valid_emails_filename, e)
          valid_emails = set()
        LOGGER.info('valid_emails: %d', len(valid_emails))
        LOGGER.info('valid_email_domains: %s', valid_email_domains)
        flask_auth0.auth0.is_valid_email = EmailValidator(
          valid_emails=valid_emails,
          valid_email_domains=valid_email_domains
        )

  update_auth()

  @blueprint.route("/")
  def _api_root() -> Response:
    return jsonify({
      'links': {
        'recommend-reviewers': url_for('api._recommend_reviewers_api'),
        'subject-areas': url_for('api._subject_areas_api'),
        'keywords': url_for('api._keywords_api'),
        'config': url_for('api._config_api')
      }
    })

  @memory.cache
  def recommend_reviewers_as_json(manuscript_no, subject_area, keywords, abstract, role, limit) \
    -> Response:
    with db.session.begin():
      return jsonify(recommend_reviewers.recommend(
        manuscript_no,
        subject_area,
        keywords,
        abstract,
        role=role,
        limit=limit
      ))

  @blueprint.route("/recommend-reviewers")
  @wrap_with_auth
  def _recommend_reviewers_api() -> Response:
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

  @blueprint.route("/subject-areas")
  def _subject_areas_api() -> Response:
    with db.session.begin():
      return jsonify(list(recommend_reviewers.get_all_subject_areas()))

  @blueprint.route("/keywords")
  def _keywords_api() -> Response:
    with db.session.begin():
      return jsonify(list(recommend_reviewers.get_all_keywords()))

  @blueprint.route("/config")
  def _config_api() -> Response:
    return jsonify(client_config)

  def reload_api():
    recommend_reviewers.reload()
    recommend_reviewers_as_json.clear()
    update_auth()

  return blueprint, reload_api
