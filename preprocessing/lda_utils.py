from time import time
from collections import namedtuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation

LdaResult = namedtuple('LdaResult', ['docvecs', 'vectorized', 'vectorizer', 'lda'])

def isstr(s):
  return isinstance(s, str)

def train_lda(data, vectorizer=None, lda=None, n_features=1000, n_topics=10):
  if vectorizer is None:
    vectorizer = TfidfVectorizer(
      max_df=0.95,
      min_df=2,
      max_features=n_features,
      stop_words='english')
  t0 = time()
  indices = [x is not None and isstr(x) and len(x) > 0 for x in data]
  indices = np.arange(len(data))[indices]
  vectorized = vectorizer.fit_transform(data[indices])
  print("vectorized in %0.3fs." % (time() - t0))

  if lda is None:
    lda = LatentDirichletAllocation(
      n_topics=n_topics,
      max_iter=5,
      learning_method='online',
      learning_offset=50.,
      random_state=0)
  t0 = time()
  matching_docvecs = list(lda.fit_transform(vectorized))
  docvecs = [None] * len(data)
  print("indices:", indices)
  for index, docvec in zip(indices, matching_docvecs):
    docvecs[index] = docvec
  print("lda in %0.3fs." % (time() - t0))
  return LdaResult(docvecs=docvecs, vectorized=vectorized, vectorizer=vectorizer, lda=lda)
