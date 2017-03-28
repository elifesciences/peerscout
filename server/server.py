from os.path import abspath
import os
import datetime

import json
from flask import Flask, request, send_from_directory, jsonify, url_for
from flask.json import JSONEncoder
from flask_cors import CORS
from joblib import Memory

from datasets import PickleDatasetLoader, CachedDatasetLoader
from services import (
  ManuscriptModel,
  DocumentSimilarityModel,
  RecommendReviewers
)

from docvec_model_proxy import DocvecModelUtils # pylint: disable=E0611

CLIENT_FOLDER = '../client/dist'


port = 8080
data_dir = os.path.join('..', '.data')
cache_dir = os.path.join(data_dir, 'server-cache')

with open('config.json') as config_file:
  config = json.load(config_file)
  port = config.get('port', port)

memory = Memory(cachedir=cache_dir, verbose=0)
print("cache directory:", cache_dir)
memory.clear(warn=False)

def load_recommender():
  csv_path = abspath(config['csv']['path'])
  datasets = CachedDatasetLoader(PickleDatasetLoader(csv_path))
  lda_docvec_predict_model = DocvecModelUtils.load_predict_model(
    os.path.join(csv_path, 'manuscript-abstracts-sense2vec-lda-docvecs-model.pickle')
  )
  doc2vec_docvec_predict_model = DocvecModelUtils.load_predict_model(
    os.path.join(csv_path, 'manuscript-abstracts-sense2vec-doc2vec-model.pickle')
  )
  manuscript_model = ManuscriptModel(datasets)
  similarity_model = DocumentSimilarityModel(
    datasets, manuscript_model=manuscript_model,
    lda_docvec_predict_model=lda_docvec_predict_model,
    doc2vec_docvec_predict_model=doc2vec_docvec_predict_model
  )
  return RecommendReviewers(
    datasets, manuscript_model=manuscript_model, similarity_model=similarity_model
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

@app.route("/api/")
def api_root():
  return jsonify({
    'links': {
      'recommend-reviewers': url_for('recommend_reviewers_api'),
      'run': url_for('run')
    }
  })

@memory.cache
def recommend_reviewers_as_json(manuscript_no, subject_area, keywords, abstract, limit):
  return jsonify(recommend_reviewers.recommend(
    manuscript_no,
    subject_area,
    keywords,
    abstract,
    limit=limit
  ))

@app.route("/api/recommend-reviewers")
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
    limit=limit
  )

@app.route("/api/subject-areas")
def subject_areas_api():
  return jsonify(list(recommend_reviewers.get_all_subject_areas()))

@app.route("/api/keywords")
def keywords_api():
  return jsonify(list(recommend_reviewers.get_all_keywords()))

@app.route("/api/hello")
def run():
  return "Hello!"

@app.route("/control/reload", methods=['POST'])
def control_reload():
  global recommend_reviewers
  if request.remote_addr != '127.0.0.1':
    return jsonify({'ip': request.remote_addr}), 403
  print("reloading...")
  recommend_reviewers = load_recommender()
  recommend_reviewers_as_json.clear()
  return jsonify({'status': 'OK'})

@app.route('/')
def send_index():
  return app.send_static_file('index.html')

@app.route('/<path:path>')
def send_client_files(path):
  return send_from_directory(CLIENT_FOLDER, path)

if __name__ == "__main__":
  app.run(port=port)
