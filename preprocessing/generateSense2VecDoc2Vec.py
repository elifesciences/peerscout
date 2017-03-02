from os.path import splitext

import pandas as pd
from sklearn.pipeline import Pipeline

from docvec_model_proxy import ( # pylint: disable=E0611
  SpacyTransformer,
  Doc2VecTransformer,
  DocvecModelUtils
)

predict_model = None
internal_predict_model = None

def process_csv_file(input_filename, output_filename, column_name, vec_size=100, n_epochs=10):
  global predict_model, internal_predict_model

  model_filename = "{}-model{}".format(*splitext(output_filename))
  print("input_filename:", input_filename)
  df = pd.read_csv(input_filename, low_memory=False)
  df = df[
    pd.notnull(df[column_name])
  ]
  texts = df[column_name].values

  if predict_model is None:
    prep_steps = [
      ('spacy', SpacyTransformer())
    ]
    final_steps = [
      ('doc2vec', Doc2VecTransformer(n_epochs=n_epochs, vec_size=vec_size))
    ]
    predict_model = Pipeline(prep_steps + final_steps)
    internal_predict_model = Pipeline(final_steps)
    docvecs = internal_predict_model.fit_transform(texts)

    print("writing model to:", model_filename)
    DocvecModelUtils.save_predict_model(predict_model, model_filename)
  else:
    # a bit of a hack to use the already trained model
    docvecs = internal_predict_model.transform(texts)

  df[column_name + '-docvecs'] = list(docvecs)
  df = df.drop(column_name, axis=1)
  print("writing dataframe to:", output_filename)
  df.to_pickle(output_filename)

N_TOPICS = 20
SUFFIX = '-sense2vec'
OUTPUT_SUFFIX = '-doc2vec'

def process_article_abstracts(csv_path, suffix=SUFFIX):
  process_csv_file(
    input_filename=csv_path + '/manuscript-abstracts{}.csv'.format(suffix),
    output_filename=csv_path + '/manuscript-abstracts{}{}.pickle'.format(suffix, OUTPUT_SUFFIX),
    column_name='abstract' + suffix
  )

def process_article_contents(csv_path, suffix=SUFFIX):
  process_csv_file(
    input_filename=csv_path + '/article-content{}.csv'.format(suffix),
    output_filename=csv_path + '/article-content{}{}.pickle'.format(suffix, OUTPUT_SUFFIX),
    column_name='content' + suffix
  )

def process_crossref_person_extra_abstracts(csv_path, suffix=SUFFIX):
  process_csv_file(
    input_filename=csv_path + '/crossref-person-extra{}.csv'.format(suffix),
    output_filename=csv_path + '/crossref-person-extra{}{}.pickle'.format(suffix, OUTPUT_SUFFIX),
    column_name='abstract' + suffix
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
