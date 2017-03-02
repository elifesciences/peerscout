import pickle

from sklearn.pipeline import Pipeline

def create_lda_predict_model(spacy_transformer, vectorizer, lda):
  return Pipeline([
    ('spacy', spacy_transformer),
    ('vectorizer', vectorizer),
    ('lda', lda)
  ])

def create_pipeline_model(pipeline):
  return pipeline

def save_predict_model(predict_model, filename):
  pickle.dump(predict_model, open(filename, "wb"))

def load_predict_model(filename):
  return pickle.load(open(filename, "rb"))
