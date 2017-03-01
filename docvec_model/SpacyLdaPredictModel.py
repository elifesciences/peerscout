import pickle

from sklearn.pipeline import Pipeline

def create_predict_model(spacy_transformer, vectorizer, lda):
  return Pipeline([
    ('spacy', spacy_transformer),
    ('vectorizer', vectorizer),
    ('lda', lda)
  ])

def save_predict_model(predict_model, filename):
  pickle.dump(predict_model, open(filename, "wb"))

def load_predict_model(filename):
  return pickle.load(open(filename, "rb"))
