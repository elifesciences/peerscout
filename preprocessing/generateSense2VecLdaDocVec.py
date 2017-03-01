from os.path import splitext

import pandas as pd
from sklearn.pipeline import Pipeline

from docvec_model_proxy import SpacyTransformer, SpacyLdaPredictModel, lda_utils # pylint: disable=E0611

train_lda = lda_utils.train_lda

predict_model = None
internal_predict_model = None

def process_csv_file(input_filename, output_filename, column_name, n_topics=10):
  global predict_model, internal_predict_model

  model_filename = "{}-model{}".format(*splitext(output_filename))
  print("input_filename:", input_filename)
  df = pd.read_csv(input_filename, low_memory=False)

  if predict_model is None:
    lda_result = train_lda(df[column_name].values, n_topics=n_topics)
    docvecs = lda_result.docvecs
    predict_model = SpacyLdaPredictModel.create_predict_model(
      spacy_transformer=SpacyTransformer(),
      vectorizer=lda_result.vectorizer,
      lda=lda_result.lda
    )
    internal_predict_model = Pipeline([
      ('vectorizer', lda_result.vectorizer),
      ('lda', lda_result.lda)
    ])
    print("writing model to:", model_filename)
    SpacyLdaPredictModel.save_predict_model(predict_model, model_filename)
  else:
    # a bit of a hack to use the already trained model
    docvecs = internal_predict_model.transform(df[column_name].values)

  df[column_name + '-docvecs'] = list(docvecs)
  df = df.drop(column_name, axis=1)
  print("writing dataframe to:", output_filename)
  df.to_pickle(output_filename)

N_TOPICS = 20
SUFFIX = '-sense2vec'
LDA_SUFFIX = '-lda-docvecs'

def process_article_abstracts(csv_path, suffix=SUFFIX, n_topics=N_TOPICS):
  process_csv_file(
    input_filename=csv_path + '/manuscript-abstracts{}.csv'.format(suffix),
    output_filename=csv_path + '/manuscript-abstracts{}{}.pickle'.format(suffix, LDA_SUFFIX),
    column_name='abstract' + suffix,
    n_topics=n_topics
  )

def process_article_contents(csv_path, suffix=SUFFIX, n_topics=N_TOPICS):
  process_csv_file(
    input_filename=csv_path + '/article-content{}.csv'.format(suffix),
    output_filename=csv_path + '/article-content{}{}.pickle'.format(suffix, LDA_SUFFIX),
    column_name='content' + suffix,
    n_topics=n_topics
  )

def process_crossref_person_extra_abstracts(csv_path, suffix=SUFFIX, n_topics=N_TOPICS):
  process_csv_file(
    input_filename=csv_path + '/crossref-person-extra{}.csv'.format(suffix),
    output_filename=csv_path + '/crossref-person-extra{}{}.pickle'.format(suffix, LDA_SUFFIX),
    column_name='abstract' + suffix,
    n_topics=n_topics
  )

def main():

  include_contents = False

  # csv_path = "./csv-small"
  csv_path = "../../csv"

  process_article_abstracts(csv_path)

  if include_contents:
    process_article_contents(csv_path)

  process_crossref_person_extra_abstracts(csv_path)


if __name__ == "__main__":
  main()
