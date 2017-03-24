import re

import pandas as pd
import spacy
from tqdm import tqdm

from convertUtils import unescape_and_strip_tags, flatten

from preprocessingUtils import get_db_path

def manuscript_number_to_no(x):
  return x.split('-')[-1]

def version_key_to_no(x):
  return 1 + int(x.split('|')[-1])

def extract_unique_keywords(series):
  return sorted(set(flatten(series.apply(
    lambda x: set(x.split(' ')) if x is not None else set()).values)))

def process_manuscript_versions(csv_path, extract_keywords_from_list):
  input_filename = csv_path + '/manuscript-versions.csv'
  output_filename = csv_path + '/manuscript-abstracts-spacy.csv'
  df = pd.read_csv(input_filename, low_memory=False)
  df['manuscript-no'] = df['base-manuscript-number'].apply(manuscript_number_to_no)
  df['version-no'] = df['version-key'].apply(version_key_to_no)
  df['abstract-spacy'] = extract_keywords_from_list(df['abstract'].values)
  df = df[[
    'manuscript-no', 'version-no',
    'abstract-spacy',
    'base-manuscript-number', 'manuscript-number', 'version-key'
  ]]
  # print("keywords:", extract_unique_keywords(df['abstract-spacy']))
  print("writing csv to:", output_filename)
  df.to_csv(output_filename, index=False)

def process_article_contents(csv_path, extract_keywords_from_list):
  input_filename = csv_path + '/article-content.csv'
  output_filename = csv_path + '/article-content-spacy.csv'
  df = pd.read_csv(input_filename, low_memory=False)
  df['content-spacy'] = extract_keywords_from_list(df['content'].values)
  df = df[[
    'manuscript-no', 'version-no',
    'content-spacy'
  ]]
  # print("keywords:", extract_unique_keywords(df['content-spacy']))
  print("writing csv to:", output_filename)
  df.to_csv(output_filename, index=False)

def process_crossref_person_extra_abstracts(csv_path, extract_keywords_from_list):
  input_filename = csv_path + '/crossref-person-extra.csv'
  output_filename = csv_path + '/crossref-person-extra-spacy.csv'
  df = pd.read_csv(input_filename, low_memory=False)
  df = df[
    df['abstract'].notnull()
  ]
  df['abstract-spacy'] = extract_keywords_from_list(df['abstract'].values)
  df = df[['doi', 'abstract-spacy']]
  # print("keywords:", extract_unique_keywords(df['content-spacy']))
  print("writing csv to:", output_filename)
  df.to_csv(output_filename, index=False)

def main():
  tqdm.pandas()

  split_pattern = re.compile(r'\s-\s|,|[^\w\s]|/|’\s')
  keyword_pattern = re.compile(r'^[a-zA-Z][^()\[\]+_%.\'0-9]+$')
  keyword_replace_pattern = re.compile(r'(a|th[aei][a-z]*|all|o|n|\s+)(\s)')

  print("loading spacy...")
  nlp = spacy.load('en')
  print("done")

  def extract_keywords_from_doc(doc):
    keywords = [
      chunk.lemma_.strip()
      for chunk in doc.noun_chunks
    ]
    keywords = flatten([split_pattern.split(s) for s in keywords])
    for _ in range(2):
      keywords = [
        keyword_replace_pattern.sub(r'\2', s).strip() for s in keywords
      ]
    keywords = [
      keyword
      for keyword in keywords
      if len(keyword) > 3 and keyword_pattern.match(keyword)
    ]
    # print(keywords)
    return ' '.join([keyword.replace(' ', '_') for keyword in keywords])

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
      result[item[0]] = extract_keywords_from_doc(doc)
    return result

  include_contents = False

  csv_path = get_db_path()

  # process_manuscript_versions(csv_path, extract_keywords_from_list)
  if include_contents:
    process_article_contents(csv_path, extract_keywords_from_list)

  process_crossref_person_extra_abstracts(
    csv_path, extract_keywords_from_list
  )


if __name__ == "__main__":
  main()
