import logging

import gensim

NAME = 'Doc2VecTransformer'

# Doc2Vec sklearn wrapper
class Doc2VecTransformer(object):
  def __init__(self, n_epochs=50, vec_size=100, window=10):
    self.n_epochs = n_epochs
    self.vec_size = vec_size
    self.window = window
    self.model = None

  def transform(self, X):
    words_by_sentence = [
      s.split(' ')
      for s in X
    ]
    return [
      self.model.infer_vector(words)
      for words in words_by_sentence
    ]

  def fit(self, X, y=None):
    return self.fit_transform(X, y)

  def fit_transform(self, X, y=None):
    words_by_sentence = [
      s.split(' ')
      for s in X
    ]

    sentences = [
      gensim.models.doc2vec.TaggedDocument(words=words, tags=[i])
      for i, words in enumerate(words_by_sentence)
    ]

    model = gensim.models.Doc2Vec(
      size=self.vec_size,
      window=self.window,
      min_count=5,
      workers=2,
      alpha=0.025,
      min_alpha=0.025,
      seed=0
    )
    self.model = model
    model.build_vocab(sentences)
    current_epoch = 0

    logger = logging.getLogger(NAME)

    for _ in range(self.n_epochs):
      logger.info("epoch: %d, alpha: %f", current_epoch, model.alpha)
      model.train(sentences)
      model.alpha = model.alpha * 0.95 # decrease the learning rate
      model.min_alpha = model.alpha # fix the learning rate, no deca
      current_epoch += 1

    return model.docvecs
