import pandas as pd

from docvec_model_proxy import lda_utils # pylint: disable=E0611

from preprocessingUtils import get_db_path

train_lda = lda_utils.train_lda

def process_csv_file(input_filename, output_filename, column_name, n_topics=10):
  print("input_filename:", input_filename)
  df = pd.read_csv(input_filename, low_memory=False)
  df[column_name + '-docvecs'] = list(train_lda(df[column_name].values).docvecs)
  df = df.drop(column_name, axis=1)
  print("writing dataframe to:", output_filename)
  df.to_pickle(output_filename)

def process_article_abstracts(csv_path):
  process_csv_file(
    input_filename=csv_path + '/manuscript-abstracts-spacy.csv',
    output_filename=csv_path + '/manuscript-abstracts-spacy-docvecs.pickle',
    column_name='abstract-spacy',
    n_topics=20
  )

def process_article_contents(csv_path):
  process_csv_file(
    input_filename=csv_path + '/article-content-spacy.csv',
    output_filename=csv_path + '/article-content-spacy-docvecs.pickle',
    column_name='content-spacy'
  )

def process_crossref_person_extra_abstracts(csv_path):
  process_csv_file(
    input_filename=csv_path + '/crossref-person-extra-spacy.csv',
    output_filename=csv_path + '/crossref-person-extra-spacy-docvecs.pickle',
    column_name='abstract-spacy'
  )

def main():

  include_contents = False

  csv_path = get_db_path()

  process_article_abstracts(csv_path)

  if include_contents:
    process_article_contents(csv_path)

  process_crossref_person_extra_abstracts(csv_path)


if __name__ == "__main__":
  main()
