import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from .utils import filter_by

MANUSCRIPT_VERSION_ID = 'manuscript-version-id'

ABSTRACT_DOCVEC_COLUMN = 'abstract-docvec'
SIMILARITY_COLUMN = 'similarity'

def load_docvecs(datasets, manuscript_model, suffix):
  abstract_docvecs_all_df = manuscript_model.add_manuscript_version_id(
    datasets["manuscript-abstracts" + suffix]\
    .rename(columns={'abstract-sense2vec-docvecs': ABSTRACT_DOCVEC_COLUMN}).dropna())
  abstract_docvecs_df = filter_by(
    abstract_docvecs_all_df,
    MANUSCRIPT_VERSION_ID,
    manuscript_model.get_valid_manuscript_version_ids()
  )
  print("valid docvecs:", len(abstract_docvecs_df))

  crossref_abstract_docvecs_df = (
    datasets["crossref-person-extra" + suffix]
    .rename(columns={
      'abstract-sense2vec-docvecs': ABSTRACT_DOCVEC_COLUMN,
      'doi': MANUSCRIPT_VERSION_ID
    }).dropna()
  )
  crossref_abstract_docvecs_df[MANUSCRIPT_VERSION_ID] = (
    crossref_abstract_docvecs_df[MANUSCRIPT_VERSION_ID].str.lower()
  )
  abstract_docvecs_df = pd.concat([
    abstract_docvecs_df,
    crossref_abstract_docvecs_df
  ])
  # this can result in duplicates, keep the first version (not crossref)
  abstract_docvecs_df = abstract_docvecs_df.drop_duplicates(
    subset=MANUSCRIPT_VERSION_ID, keep='first'
  )
  print("docvecs incl crossref:", len(abstract_docvecs_df))
  return abstract_docvecs_all_df, abstract_docvecs_df

class DocumentSimilarityModel(object):
  def __init__(
    self, datasets, manuscript_model,
    lda_docvec_predict_model=None, doc2vec_docvec_predict_model=None):

    self.lda_docvec_predict_model = lda_docvec_predict_model
    self.doc2vec_docvec_predict_model = doc2vec_docvec_predict_model

    self.abstract_lda_docvecs_all_df, self.abstract_lda_docvecs_df = (
      load_docvecs(datasets, manuscript_model, "-sense2vec-lda-docvecs")
    )
    self.abstract_doc2vec_all_df, self.abstract_doc2vec_df = (
      load_docvecs(datasets, manuscript_model, "-sense2vec-doc2vec")
    )

    # self.abstract_lda_docvecs_all_df = manuscript_model.add_manuscript_version_id(
    #   datasets["manuscript-abstracts-sense2vec-lda-docvecs"]\
    #   .rename(columns={'abstract-sense2vec-docvecs': ABSTRACT_DOCVEC_COLUMN}).dropna())
    # self.abstract_lda_docvecs_df = filter_by(
    #   self.abstract_lda_docvecs_all_df,
    #   MANUSCRIPT_VERSION_ID,
    #   manuscript_model.get_valid_manuscript_version_ids()
    # )
    # print("valid docvecs:", len(self.abstract_docvecs_df))

    # crossref_abstract_docvecs_df = (
    #   datasets["crossref-person-extra-sense2vec-lda-docvecs"]
    #   .rename(columns={
    #     'abstract-sense2vec-docvecs': ABSTRACT_DOCVEC_COLUMN,
    #     'doi': MANUSCRIPT_VERSION_ID
    #   }).dropna()
    # )
    # crossref_abstract_docvecs_df[MANUSCRIPT_VERSION_ID] = (
    #   crossref_abstract_docvecs_df[MANUSCRIPT_VERSION_ID].str.lower()
    # )
    # self.abstract_docvecs_df = pd.concat([
    #   self.abstract_docvecs_df,
    #   crossref_abstract_docvecs_df
    # ])
    # print("docvecs incl crossref:", len(self.abstract_docvecs_df))

  def __find_similar_manuscripts_to_docvecs(
    self, to_lda_docvecs, to_doc2vec, exclude_version_ids=None):

    if len(to_lda_docvecs) == 0 or len(to_doc2vec) != len(to_lda_docvecs):
      return pd.DataFrame({
        MANUSCRIPT_VERSION_ID: [],
        SIMILARITY_COLUMN: []
      })
    version_ids = (
      set(self.abstract_lda_docvecs_df[MANUSCRIPT_VERSION_ID].values) |
      set(self.abstract_doc2vec_df[MANUSCRIPT_VERSION_ID].values)
    )
    if exclude_version_ids is not None:
      version_ids = version_ids - set(exclude_version_ids)
    version_ids = list(version_ids)
    other_lda_docvecs = np.array(
      self.abstract_lda_docvecs_df.set_index(MANUSCRIPT_VERSION_ID)[ABSTRACT_DOCVEC_COLUMN]
      .loc[version_ids].values.tolist()
    )
    other_doc2vec_docvecs = np.array(
      self.abstract_doc2vec_df.set_index(MANUSCRIPT_VERSION_ID)[ABSTRACT_DOCVEC_COLUMN]
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
      MANUSCRIPT_VERSION_ID: version_ids,
      SIMILARITY_COLUMN: combined_similarity
    })
    if exclude_version_ids is not None:
      similarity = similarity[
        ~similarity[MANUSCRIPT_VERSION_ID].isin(
          exclude_version_ids
        )
      ]
    return similarity

  def find_similar_manuscripts_to_abstract(self, abstract):
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
    to_lda_docvecs = self.abstract_lda_docvecs_all_df[
      self.abstract_lda_docvecs_all_df[MANUSCRIPT_VERSION_ID].isin(
        version_ids
      )
    ][ABSTRACT_DOCVEC_COLUMN].values
    to_doc2vec_docvecs = self.abstract_doc2vec_all_df[
      self.abstract_doc2vec_all_df[MANUSCRIPT_VERSION_ID].isin(
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
