import re
import logging

import spacy
from tqdm import tqdm

NAME = 'SpacyTransformer'

LABELS = {
  'ENT': 'ENT',
  'PERSON': 'ENT',
  'NORP': 'ENT',
  'FAC': 'ENT',
  'ORG': 'ENT',
  'GPE': 'ENT',
  'LOC': 'ENT',
  'LAW': 'ENT',
  'PRODUCT': 'ENT',
  'EVENT': 'ENT',
  'WORK_OF_ART': 'ENT',
  'LANGUAGE': 'ENT',
  'DATE': 'DATE',
  'TIME': 'TIME',
  'PERCENT': 'PERCENT',
  'MONEY': 'MONEY',
  'QUANTITY': 'QUANTITY',
  'ORDINAL': 'ORDINAL',
  'CARDINAL': 'CARDINAL'
}

IGNORE_TAGS = set([
  'PUNCT',
  'SPACE',
  'VERB',
  'ADP',
  'PART',
  'PRON',
  'ADV',
  'ADJ',
  'DET',
  'CONJ'
])

IGNORE_TYPES = set([
  'CARDINAL'
])

def represent_word(word):
  if word.like_url:
    return '%%URL|X'
  text = re.sub(r'\s', '_', word.lemma_)
  tag = LABELS.get(word.ent_type_, word.pos_)
  if not tag:
    tag = '?'
  return text.lower() + '|' + tag

def noun_with_mod_tokens(token):
  result = [token]
  for c in reversed(list(token.children)):
    if c.dep_ not in ('advmod', 'amod', 'compound'):
      break
    result.append(c)
  return list(reversed(result))

def transform_doc(doc):
  strings = []
  for sent in doc.sents:
    sent_strings = []
    for w in sent:
      if w.pos_ in ('NOUN', 'PROPN'):
        compound_tokens = noun_with_mod_tokens(w)
        # include individual tokens
        for t in compound_tokens:
          # don't include compound nouns multiple times
          if len(compound_tokens) > 1 or t.dep_ not in ('compound'):
            sent_strings.append(represent_word(t))
        if len(compound_tokens) > 1:
          # include the whole noun phrase
          sent_strings.append('_'.join([
            t.lemma_ for t in compound_tokens
          ]) + '|' + LABELS.get(w.ent_type_, w.pos_))
      elif w.pos_ not in IGNORE_TAGS and w.ent_type_ not in IGNORE_TYPES:
        sent_strings.append(represent_word(w))
    if len(sent_strings) > 0:
      strings.append(' '.join(sent_strings))
  if strings:
    return '\n'.join(strings) + '\n'
  else:
    return ''

global_nlp = None

def get_nlp():
  global global_nlp
  if global_nlp is None:
    logger = logging.getLogger(NAME)
    logger.debug("loading spacy...")
    global_nlp = spacy.load('en')
    logger.debug("done")
  return global_nlp

class SpacyTransformer(object):
  def __init__(self, use_pipe=False, use_progress=None):
    self.use_pipe = use_pipe
    self.use_progress = use_progress

  def transform(self, X):
    nlp = get_nlp()
    valid_strings = [
      (i, text)
      for i, text in enumerate(X)
      if isinstance(text, str)
    ]
    valid_text_list = [text for _, text in valid_strings]

    if self.use_pipe:
      source_list = nlp.pipe(
        valid_text_list,
        n_threads=2,
        batch_size=10
      )
    else:
      source_list = [nlp(text) for text in valid_text_list]

    if self.use_progress:
      source_list = tqdm(source_list, total=len(valid_strings))

    result = [None] * len(X)
    for item, doc in zip(valid_strings, source_list):
      result[item[0]] = transform_doc(doc)

    return result

  def fit(self, X, y=None):
    # do nothing, there is no fitting
    return
