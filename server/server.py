from os.path import abspath
import datetime

import json
from flask import Flask, request, send_from_directory, jsonify, url_for
from flask.json import JSONEncoder
from flask_cors import CORS
# from intend_matchers.simple_intend_matcher import SimpleIntendMatcher

from datasets import\
  CsvDatasetLoader, PickleDatasetLoader,\
  RoutingDatasetLoader, CachedDatasetLoader
from services import RecommendReviewers

CLIENT_FOLDER = '../client/dist'

port = 8080

with open('config.json') as config_file:
  config = json.load(config_file)
  csv_path = abspath(config['csv']['path'])
  csv_datasets = CsvDatasetLoader(csv_path)
  pickle_datasets = PickleDatasetLoader(csv_path)
  routing_datasets = RoutingDatasetLoader({
    'manuscript-abstracts-spacy-docvecs': pickle_datasets,
    'crossref-person-extra-spacy-docvecs': pickle_datasets
  }, csv_datasets)
  datasets = CachedDatasetLoader(routing_datasets)
  recommend_reviewers = RecommendReviewers(datasets)
  if 'port' in config:
    port = config['port']

class CustomJSONEncoder(JSONEncoder):
  def default(self, obj):
    try:
      if isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date):
        return obj.isoformat()
    except TypeError:
      pass
    return JSONEncoder.default(self, obj)

app = Flask(__name__, static_folder=CLIENT_FOLDER)
app.json_encoder = CustomJSONEncoder
CORS(app)

@app.route("/api/")
def api_root():
  return jsonify({
    'links': {
      'recommend-reviewers': url_for('recommend_reviewers_api'),
      'run': url_for('run')
    }
  })

@app.route("/api/recommend-reviewers")
def recommend_reviewers_api():
  keywords = request.args.get('keywords')
  manuscript_no = request.args.get('manuscript_no')
  if keywords is None:
    return 'keywords parameter required', 400
  result = recommend_reviewers.recommend(keywords, manuscript_no)
  # print("result:", result)
  # if result is None:
  #   return 'did not match any intend', 404
  return jsonify(result)

@app.route("/api/hello")
def run():
  return "Hello!"

@app.route('/')
def send_index():
  return app.send_static_file('index.html')

@app.route('/<path:path>')
def send_client_files(path):
  return send_from_directory(CLIENT_FOLDER, path)

if __name__ == "__main__":
  app.run(port=port)
