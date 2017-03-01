from time import time
from collections import namedtuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

LdaResult = namedtuple('LdaResult', ['docvecs', 'vectorized', 'vectorizer', 'lda'])

def isstr(s):
  return isinstance(s, str)

def get_default_stop_words():
  return ENGLISH_STOP_WORDS

def tokenize_terms(text):
    return text.split(' ')

def train_lda(
  data,
  vectorizer=None,
  vectorized=None,
  lda=None,
  n_features=100,
  n_topics=10,
  max_df=0.90,
  min_df=10,
  stop_words='english',
  max_iter=10,
  learning_offset=50,
  learning_method='batch'):

  if vectorizer is None:
    vectorizer = TfidfVectorizer(
      max_df=max_df,
      min_df=min_df,
      max_features=n_features,
      stop_words=stop_words,
      tokenizer=tokenize_terms)
  indices = [x is not None and isstr(x) and len(x) > 0 for x in data]
  indices = np.arange(len(data))[indices]
  if vectorized is None:
    t0 = time()
    vectorized = vectorizer.fit_transform(data[indices])
    print("vectorized in %0.3fs." % (time() - t0))

  if lda is None:
    lda = LatentDirichletAllocation(
      n_topics=n_topics,
      max_iter=max_iter,
      learning_method=learning_method,
      learning_offset=learning_offset,
      random_state=0)
  t0 = time()
  matching_docvecs = list(lda.fit_transform(vectorized))
  docvecs = [None] * len(data)
  # print("indices:", indices)
  for index, docvec in zip(indices, matching_docvecs):
    docvecs[index] = docvec
  print("lda in %0.3fs." % (time() - t0))
  return LdaResult(docvecs=docvecs, vectorized=vectorized, vectorizer=vectorizer, lda=lda)
