import logging

import gensim

NAME = 'Doc2VecTransformer'

# Doc2Vec sklearn wrapper
class Doc2VecTransformer(object):
  def __init__(
    self, n_epochs=50, vec_size=100, window=10, min_count=5, workers=2, seed=1):

    self.n_epochs = n_epochs
    self.vec_size = vec_size
    self.window = window
    self.min_count = min_count
    self.workers = workers
    self.seed = seed
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
    logger = logging.getLogger(NAME)

    words_by_sentence = [
      s.split(' ')
      for s in X
    ]

    logging.debug('words_by_sentence: %.100s...', words_by_sentence)

    sentences = [
      gensim.models.doc2vec.TaggedDocument(words=words, tags=[i])
      for i, words in enumerate(words_by_sentence)
    ]

    model = gensim.models.Doc2Vec(
      size=self.vec_size,
      window=self.window,
      min_count=self.min_count,
      workers=self.workers,
      alpha=0.025,
      min_alpha=0.025,
      seed=self.seed
    )
    self.model = model
    model.build_vocab(sentences)
    current_epoch = 0

    for _ in range(self.n_epochs):
      logger.info("epoch: %d, alpha: %f", current_epoch, model.alpha)
      model.train(
        sentences,
        total_examples=len(sentences),
        epochs=1
      )
      model.alpha = model.alpha * 0.95 # decrease the learning rate
      model.min_alpha = model.alpha # fix the learning rate, no deca
      current_epoch += 1

    return model.docvecs
