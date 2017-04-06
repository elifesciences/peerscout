import pickle

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from .utils import filter_by

VERSION_ID = 'version_id'

ABSTRACT_DOCVEC_COLUMN = 'abstract-docvec'
SIMILARITY_COLUMN = 'similarity'

def load_docvecs(db, manuscript_model, column_name):
  ml_manuscript_data_table = db['ml_manuscript_data']
  docvec_column = getattr(ml_manuscript_data_table.table, column_name)

  # Find out whether we need to update anything at all
  abstract_docvecs_all_df = pd.DataFrame(db.session.query(
    ml_manuscript_data_table.table.version_id,
    docvec_column
  ).filter(
    docvec_column != None
  ).all(), columns=[VERSION_ID, ABSTRACT_DOCVEC_COLUMN])

  abstract_docvecs_df = filter_by(
    abstract_docvecs_all_df,
    VERSION_ID,
    manuscript_model.get_valid_manuscript_version_ids()
  )
  print("valid docvecs:", len(abstract_docvecs_df))

  return abstract_docvecs_all_df, abstract_docvecs_df

class DocumentSimilarityModel(object):
  def __init__(
    self, db, manuscript_model,
    lda_docvec_predict_model=None, doc2vec_docvec_predict_model=None):

    self.lda_docvec_predict_model = lda_docvec_predict_model
    self.doc2vec_docvec_predict_model = doc2vec_docvec_predict_model

    self.abstract_lda_docvecs_all_df, self.abstract_lda_docvecs_df = (
      load_docvecs(db, manuscript_model, 'lda_docvec')
    )
    self.abstract_doc2vec_all_df, self.abstract_doc2vec_df = (
      load_docvecs(db, manuscript_model, 'doc2vec_docvec')
    )

  def __empty_similarity_result(self):
    return pd.DataFrame({
      VERSION_ID: [],
      SIMILARITY_COLUMN: []
    })

  def __find_similar_manuscripts_to_docvecs(
    self, to_lda_docvecs, to_doc2vec, exclude_version_ids=None):

    if len(to_lda_docvecs) == 0 or len(to_doc2vec) != len(to_lda_docvecs):
      return self.__empty_similarity_result()
    version_ids = (
      set(self.abstract_lda_docvecs_df[VERSION_ID].values) &
      set(self.abstract_doc2vec_df[VERSION_ID].values)
    )
    if exclude_version_ids is not None:
      version_ids = version_ids - set(exclude_version_ids)
    version_ids = list(version_ids)
    other_lda_docvecs = np.array(
      self.abstract_lda_docvecs_df.set_index(VERSION_ID)[ABSTRACT_DOCVEC_COLUMN]
      .loc[version_ids].values.tolist()
    )
    other_doc2vec_docvecs = np.array(
      self.abstract_doc2vec_df.set_index(VERSION_ID)[ABSTRACT_DOCVEC_COLUMN]
      .loc[version_ids].values.tolist()
    )
    to_lda_docvecs = np.array(to_lda_docvecs)
    to_doc2vec = np.array(to_doc2vec)
    lda_similarity = cosine_similarity(
      other_lda_docvecs,\
      to_lda_docvecs
    )[:, 0].reshape(-1)
    doc2vec_similarity = cosine_similarity(
      other_doc2vec_docvecs,\
      to_doc2vec
    )[:, 0].reshape(-1)
    print("lda_similarity:", lda_similarity.shape)
    print("doc2vec_similarity:", doc2vec_similarity.shape)
    combined_similarity = (lda_similarity + doc2vec_similarity) / 2
    print("combined_similarity:", combined_similarity.shape)
    similarity = pd.DataFrame({
      VERSION_ID: version_ids,
      SIMILARITY_COLUMN: combined_similarity
    })
    if exclude_version_ids is not None:
      similarity = similarity[
        ~similarity[VERSION_ID].isin(
          exclude_version_ids
        )
      ]
    return similarity

  def is_incomplete_model(self):
    return (
      self.lda_docvec_predict_model is None or
      self.doc2vec_docvec_predict_model is None
    )

  def find_similar_manuscripts_to_abstract(self, abstract):
    if self.is_incomplete_model():
      return self.__empty_similarity_result()
    to_lda_docvecs = (
      self.lda_docvec_predict_model.transform([abstract])
      if self.lda_docvec_predict_model is not None
      else []
    )
    to_doc2vec_docvecs = (
      self.doc2vec_docvec_predict_model.transform([abstract])
      if self.doc2vec_docvec_predict_model is not None
      else []
    )
    print("abstract docvec:", to_lda_docvecs, abstract)
    return self.__find_similar_manuscripts_to_docvecs(to_lda_docvecs, to_doc2vec_docvecs)

  def find_similar_manuscripts(self, version_ids):
    if self.is_incomplete_model():
      return self.__empty_similarity_result()
    to_lda_docvecs = self.abstract_lda_docvecs_all_df[
      self.abstract_lda_docvecs_all_df[VERSION_ID].isin(
        version_ids
      )
    ][ABSTRACT_DOCVEC_COLUMN].values
    to_doc2vec_docvecs = self.abstract_doc2vec_all_df[
      self.abstract_doc2vec_all_df[VERSION_ID].isin(
        version_ids
      )
    ][ABSTRACT_DOCVEC_COLUMN].values
    if len(to_lda_docvecs) == 0 or len(to_doc2vec_docvecs) == 0:
      print("no docvecs for:", version_ids)
    return self.__find_similar_manuscripts_to_docvecs(
      to_lda_docvecs.tolist(),
      to_doc2vec_docvecs.tolist(),
      exclude_version_ids=version_ids
    )

def load_similarity_model_from_database(db, manuscript_model):
  ml_model_data_table = db['ml_model_data']

  required_model_ids = set([
    ml_model_data_table.table.LDA_MODEL_ID,
    ml_model_data_table.table.DOC2VEC_MODEL_ID
  ])

  model_data = pd.DataFrame(db.session.query(
    ml_model_data_table.table.id,
    ml_model_data_table.table.data
  ).filter(
    ml_model_data_table.table.id.in_(required_model_ids)
  ).all(), columns=['id', 'data']).set_index('id')

  if set(model_data.index.values) != required_model_ids:
    print("Warning: required model data for {} but only found data for {}".format(
      required_model_ids, set(model_data.index.values)
    ))
    return DocumentSimilarityModel(
      db, manuscript_model=manuscript_model,
      lda_docvec_predict_model=None,
      doc2vec_docvec_predict_model=None
    )

  lda_docvec_predict_model = pickle.loads(
    model_data.ix[ml_model_data_table.table.LDA_MODEL_ID]['data']
  )
  doc2vec_docvec_predict_model = pickle.loads(
    model_data.ix[ml_model_data_table.table.DOC2VEC_MODEL_ID]['data']
  )
  similarity_model = DocumentSimilarityModel(
    db, manuscript_model=manuscript_model,
    lda_docvec_predict_model=lda_docvec_predict_model,
    doc2vec_docvec_predict_model=doc2vec_docvec_predict_model
  )
  return similarity_model
