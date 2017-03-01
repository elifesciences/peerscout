import re

import pandas as pd
import spacy
from tqdm import tqdm

from convertUtils import unescape_and_strip_tags, flatten

def manuscript_number_to_no(x):
  return x.split('-')[-1]

def version_key_to_no(x):
  return 1 + int(x.split('|')[-1])

def extract_unique_keywords(series):
  return sorted(set(flatten(series.apply(
    lambda x: set(x.split(' ')) if x is not None else set()).values)))

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

SUFFIX = '-sense2vec'


def process_manuscript_versions(
  csv_path, extract_keywords_from_list, suffix=SUFFIX):

  input_filename = csv_path + '/manuscript-versions.csv'
  output_filename = csv_path + '/manuscript-abstracts{}.csv'.format(suffix)
  df = pd.read_csv(input_filename, low_memory=False)
  df['manuscript-no'] = df['base-manuscript-number'].apply(manuscript_number_to_no)
  df['version-no'] = df['version-key'].apply(version_key_to_no)
  df = df[
    df['abstract'].notnull()
  ]
  df['abstract' + suffix] = extract_keywords_from_list(df['abstract'].values)
  df = df[[
    'manuscript-no', 'version-no',
    'abstract' + suffix,
    'base-manuscript-number', 'manuscript-number', 'version-key'
  ]]
  # print("keywords:", extract_unique_keywords(df['abstract-spacy']))
  print("writing csv to:", output_filename)
  df.to_csv(output_filename, index=False)

def process_article_contents(
  csv_path, extract_keywords_from_list, suffix=SUFFIX):

  input_filename = csv_path + '/article-content.csv'
  output_filename = csv_path + '/article-content{}.csv'.format(suffix)
  df = pd.read_csv(input_filename, low_memory=False)
  df = df[
    df['content'].notnull()
  ]
  df['content' + suffix] = extract_keywords_from_list(df['content'].values)
  df = df[[
    'manuscript-no', 'version-no',
    'content' + suffix
  ]]
  # print("keywords:", extract_unique_keywords(df['content-spacy']))
  print("writing csv to:", output_filename)
  df.to_csv(output_filename, index=False)

def process_crossref_person_extra_abstracts(
  csv_path, extract_keywords_from_list, suffix=SUFFIX):

  input_filename = csv_path + '/crossref-person-extra.csv'
  output_filename = csv_path + '/crossref-person-extra{}.csv'.format(suffix)
  df = pd.read_csv(input_filename, low_memory=False)
  df = df[
    df['abstract'].notnull()
  ]
  df['abstract' + suffix] = extract_keywords_from_list(df['abstract'].values)
  df = df[['doi', 'abstract' + suffix]]
  # print("keywords:", extract_unique_keywords(df['content-spacy']))
  print("writing csv to:", output_filename)
  df.to_csv(output_filename, index=False)

def main():
  tqdm.pandas()

  print("loading spacy...")
  nlp = spacy.load('en')
  print("done")

  def extract_keywords_from_list(texts):
    valid_strings = [
      (i, unescape_and_strip_tags(text))
      for i, text in enumerate(texts)
      if isinstance(text, str)
    ]
    result = [None] * len(texts)
    pbar = tqdm(nlp.pipe(
      [text for _, text in valid_strings],
      n_threads=2,
      batch_size=10
    ), total=len(valid_strings))
    for item, doc in zip(valid_strings, pbar):
      result[item[0]] = transform_doc(doc)
    return result

  include_contents = False

  # csv_path = "./csv-small"
  csv_path = "../csv"

  process_manuscript_versions(csv_path, extract_keywords_from_list)
  if include_contents:
    process_article_contents(csv_path, extract_keywords_from_list)

  process_crossref_person_extra_abstracts(
    csv_path, extract_keywords_from_list
  )


if __name__ == "__main__":
  main()
