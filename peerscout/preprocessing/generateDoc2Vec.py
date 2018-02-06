import logging

import pandas as pd
import sqlalchemy
from sklearn.pipeline import Pipeline

from ..docvec_model import (
  SpacyTransformer,
  Doc2VecTransformer,
  DocvecModelUtils
)

from ..shared.database import connect_managed_configured_database

NAME = 'generateDoc2Vec'

def configure_doc2vec_logging():
  logging.getLogger('gensim.models.doc2vec').setLevel(logging.WARNING)
  logging.getLogger('gensim.models.word2vec').setLevel(logging.WARNING)

def process_article_abstracts(db, vec_size=100, n_epochs=10):
  # We need to either:
  # a) train the model on all of the data (not just new ones)
  #    Pros: all of the data is considered
  # b) or use a pre-trained model to predict the values for new entries
  #    Pros: Faster; Vectors are more stable

  # Option a) is implemented below

  configure_doc2vec_logging()

  logger = logging.getLogger(NAME)

  ml_manuscript_data_table = db['ml_manuscript_data']

  # Find out whether we need to update anything at all
  ml_data_requiring_doc2vec_docvec_count = db.session.query(
    ml_manuscript_data_table.table
  ).filter(
    sqlalchemy.and_(
      ml_manuscript_data_table.table.abstract_tokens != None,
      ml_manuscript_data_table.table.doc2vec_docvec == None, # pylint: disable=C0121
    )
  ).count()

  if ml_data_requiring_doc2vec_docvec_count > 0:
    # Yes, get all of the data
    logger.info(
      "number of new manuscript versions requiring Doc2Vec document vectors: %d",
      ml_data_requiring_doc2vec_docvec_count
    )
    ml_data_requiring_doc2vec_docvec_df = pd.DataFrame(db.session.query(
      ml_manuscript_data_table.table.version_id,
      ml_manuscript_data_table.table.abstract_tokens
    ).filter(
      sqlalchemy.and_(
        ml_manuscript_data_table.table.abstract_tokens != None
      )
    ).all(), columns=['version_id', 'abstract_tokens'])
  else:
    ml_data_requiring_doc2vec_docvec_df = pd.DataFrame([])

  logger.info(
    "number of manuscript versions requiring Doc2Vec document vectors: %d",
    len(ml_data_requiring_doc2vec_docvec_df)
  )

  if len(ml_data_requiring_doc2vec_docvec_df) > 0:
    texts = ml_data_requiring_doc2vec_docvec_df['abstract_tokens'].values

    prep_steps = [
      ('spacy', SpacyTransformer())
    ]
    final_steps = [
      ('doc2vec', Doc2VecTransformer(n_epochs=n_epochs, vec_size=vec_size))
    ]
    predict_model = Pipeline(prep_steps + final_steps)
    internal_predict_model = Pipeline(final_steps)
    docvecs = internal_predict_model.fit_transform(texts)

    predict_model_binary = DocvecModelUtils.save_predict_model_to_binary(predict_model)

    ml_data_df = ml_data_requiring_doc2vec_docvec_df[['version_id']]
    ml_data_df['doc2vec_docvec'] = [[float(x) for x in r] for r in docvecs]
    ml_manuscript_data_table.update_list(
      ml_data_df.to_dict(orient='records')
    )

    ml_model_data_table = db['ml_model_data']
    ml_model_data_table.update_or_create(
      model_id=ml_model_data_table.table.DOC2VEC_MODEL_ID,
      data=predict_model_binary
    )

    db.commit()

def main():
  with connect_managed_configured_database() as db:

    process_article_abstracts(db)

if __name__ == "__main__":
  from ..shared.logging_config import configure_logging
  configure_logging('update')

  main()
