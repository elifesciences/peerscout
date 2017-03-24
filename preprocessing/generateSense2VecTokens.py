import pandas as pd
from tqdm import tqdm

from docvec_model_proxy import SpacyTransformer # pylint: disable=E0611

from convertUtils import unescape_and_strip_tags_if_not_none, flatten

from preprocessingUtils import get_db_path

def manuscript_number_to_no(x):
  return x.split('-')[-1]

def version_key_to_no(x):
  return 1 + int(x.split('|')[-1])

def extract_unique_keywords(series):
  return sorted(set(flatten(series.apply(
    lambda x: set(x.split(' ')) if x is not None else set()).values)))

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

  spacy_transformer = SpacyTransformer(use_pipe=True, use_progress=True)

  def extract_keywords_from_list(texts):
    return spacy_transformer.transform([
      unescape_and_strip_tags_if_not_none(s)
      for s in texts
    ])

  include_contents = False

  csv_path = get_db_path()

  process_manuscript_versions(csv_path, extract_keywords_from_list)
  if include_contents:
    process_article_contents(csv_path, extract_keywords_from_list)

  process_crossref_person_extra_abstracts(
    csv_path, extract_keywords_from_list
  )


if __name__ == "__main__":
  main()
