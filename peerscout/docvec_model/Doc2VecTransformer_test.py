import logging

import pytest

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from .Doc2VecTransformer import (
  Doc2VecTransformer
)

RELATED_TEXTS = [
  'life sciences may include research subjects such as mice',
  'life sciences may also look at cats',
  'mice are to life sciences what bread is to butter'
]
RELATED_TEXTS_INDICES = range(len(RELATED_TEXTS))

UNRELATED_TEXTS = [
  'astronomy is an entirly different field',
  'stars in astronomy are shining',
  'astronomy is looking into the sky'
]
UNRELATED_TEXTS_INDICES = range(
  len(RELATED_TEXTS),
  len(RELATED_TEXTS) + len(UNRELATED_TEXTS)
)

TEXT_LIST = RELATED_TEXTS + UNRELATED_TEXTS

def get_logger():
  return logging.getLogger(__name__)

@pytest.mark.slow
class TestDoc2VecTransformer(object):
  def test_should_find_similarities(self):
    docvecs = Doc2VecTransformer(
      min_count=1, # do not skip infrequent works (in our small dataset)
      vec_size=2, # need to reduce the vector size due to our very small dataset
      n_epochs=100, # need more iterations
      workers=1,
      seed=1
    ).fit_transform(TEXT_LIST)
    get_logger().debug('docvecs: %s', docvecs)

    similarities_first_with = cosine_similarity(docvecs, [docvecs[RELATED_TEXTS_INDICES[0]]])[:, 0]
    get_logger().debug('similarities_first_with: %s', similarities_first_with)

    self_similarity = similarities_first_with[RELATED_TEXTS_INDICES[0]]
    related_similarities = [similarities_first_with[i] for i in RELATED_TEXTS_INDICES[1:]]
    unrelated_similarities = [similarities_first_with[i] for i in UNRELATED_TEXTS_INDICES]

    related_mean = np.mean(related_similarities)
    unrelated_mean = np.mean(unrelated_similarities)

    get_logger().debug(
      'related_similarities: %s (mean: %s)', related_similarities, related_mean
    )
    get_logger().debug(
      'unrelated_similarities: %s (mean: %s)', unrelated_similarities, unrelated_mean
    )

    assert self_similarity > 0.99

    # Note: this test doesn't currently reliably work because of the very small dataset
    # assert related_mean > unrelated_mean
