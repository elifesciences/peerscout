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
    return sorted(set(flatten(series.apply(lambda x: set(x.split(' '))).values)))

def process_manuscript_versions(csv_path, extract_keywords):
  input_filename = csv_path + '/manuscript-versions.csv'
  output_filename = csv_path + '/manuscript-abstracts-spacy.csv'
  df = pd.read_csv(input_filename)
  df['manuscript-no'] = df['base-manuscript-number'].apply(manuscript_number_to_no)
  df['version-no'] = df['version-key'].apply(version_key_to_no)
  df['abstract-spacy'] = df['abstract'].progress_apply(
    lambda s: extract_keywords(s) if isinstance(s, str) else None
  )
  df = df[[
    'manuscript-no', 'version-no',
    'abstract-spacy',
    'base-manuscript-number', 'manuscript-number', 'version-key'
  ]]
  print("writing csv to:", output_filename)
  df.to_csv(output_filename)

def process_article_contents(csv_path, extract_keywords):
  input_filename = csv_path + '/article-content.csv'
  output_filename = csv_path + '/article-content-spacy.csv'
  df = pd.read_csv(input_filename)
  df['content-spacy'] = df['content'].progress_apply(
    lambda s: extract_keywords(s) if isinstance(s, str) else None
  )
  df = df[[
    'manuscript-no', 'version-no',
    'content-spacy'
  ]]
  print("keywords:", extract_unique_keywords(df['content-spacy']))
  print("writing csv to:", output_filename)
  df.to_csv(output_filename)

def main():
  print("loading spacy")
  nlp = spacy.load('en')
  print("done")

  tqdm.pandas()

  split_pattern = re.compile(r'\s-\s|,')
  keyword_pattern = re.compile(r'[a-zA-z][^()\[\]+_%.\'0-9]+')
  keyword_replace_pattern = re.compile(r'(a|th[aei][a-z]*|o|n|\s+)(\s)')

  def extract_keywords(s):
    keywords = [
      chunk.lemma_.strip()
      for chunk in nlp(unescape_and_strip_tags(s)).noun_chunks
    ]
    keywords = flatten([split_pattern.split(s) for s in keywords])
    for _ in range(2):
      keywords = [
        keyword_replace_pattern.sub(r'\2', s).strip() for s in keywords
      ]
    keywords = [
      keyword
      for keyword in keywords
      if len(keyword) > 3 and keyword_pattern.fullmatch(keyword)
    ]
    # print(keywords)
    return ' '.join([keyword.replace(' ', '_') for keyword in keywords])

  csv_path = "./csv-small"
  # csv_path = "../csv"

  process_manuscript_versions(csv_path, extract_keywords)
  process_article_contents(csv_path, extract_keywords)


if __name__ == "__main__":
  main()
