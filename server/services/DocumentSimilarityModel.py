import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from .utils import filter_by

MANUSCRIPT_VERSION_ID = 'manuscript-version-id'

ABSTRACT_DOCVEC_COLUMN = 'abstract-docvec'
SIMILARITY_COLUMN = 'similarity'


class DocumentSimilarityModel(object):
  def __init__(self, datasets, manuscript_model, docvec_predict_model=None):
    self.docvec_predict_model = docvec_predict_model

    self.abstract_docvecs_all_df = manuscript_model.add_manuscript_version_id(
      datasets["manuscript-abstracts-sense2vec-lda-docvecs"]\
      .rename(columns={'abstract-sense2vec-docvecs': ABSTRACT_DOCVEC_COLUMN}).dropna())
    self.abstract_docvecs_df = filter_by(
      self.abstract_docvecs_all_df,
      MANUSCRIPT_VERSION_ID,
      manuscript_model.get_valid_manuscript_version_ids()
    )
    print("valid docvecs:", len(self.abstract_docvecs_df))

    crossref_abstract_docvecs_df = (
      datasets["crossref-person-extra-sense2vec-lda-docvecs"]
      .rename(columns={
        'abstract-sense2vec-docvecs': ABSTRACT_DOCVEC_COLUMN,
        'doi': MANUSCRIPT_VERSION_ID
      }).dropna()
    )
    crossref_abstract_docvecs_df[MANUSCRIPT_VERSION_ID] = (
      crossref_abstract_docvecs_df[MANUSCRIPT_VERSION_ID].str.lower()
    )
    self.abstract_docvecs_df = pd.concat([
      self.abstract_docvecs_df,
      crossref_abstract_docvecs_df
    ])
    print("docvecs incl crossref:", len(self.abstract_docvecs_df))

  def __find_similar_manuscripts_to_docvecs(self, to_docvecs, exclude_version_ids=None):
    if len(to_docvecs) == 0:
      return pd.DataFrame({
        MANUSCRIPT_VERSION_ID: [],
        SIMILARITY_COLUMN: []
      })
    all_docvecs = self.abstract_docvecs_df[ABSTRACT_DOCVEC_COLUMN].values
    to_docvecs = to_docvecs.tolist()
    all_docvecs = all_docvecs.tolist()
    similarity = pd.DataFrame({
      MANUSCRIPT_VERSION_ID: self.abstract_docvecs_df[MANUSCRIPT_VERSION_ID],
      SIMILARITY_COLUMN: cosine_similarity(
        all_docvecs,\
        to_docvecs
      )[:, 0]
    })
    if exclude_version_ids is not None:
      similarity = similarity[
        ~similarity[MANUSCRIPT_VERSION_ID].isin(
          exclude_version_ids
        )
      ]
    return similarity

  def find_similar_manuscripts_to_abstract(self, abstract):
    to_docvecs = (
      self.docvec_predict_model.transform([abstract])
      if self.docvec_predict_model is not None
      else []
    )
    print("abstract docvec:", to_docvecs, abstract)
    return self.__find_similar_manuscripts_to_docvecs(to_docvecs)

  def find_similar_manuscripts(self, version_ids):
    to_docvecs = self.abstract_docvecs_all_df[
      self.abstract_docvecs_all_df[MANUSCRIPT_VERSION_ID].isin(
        version_ids
      )
    ][ABSTRACT_DOCVEC_COLUMN].values
    if len(to_docvecs) == 0:
      print("no docvecs for:", version_ids)
    return self.__find_similar_manuscripts_to_docvecs(to_docvecs, exclude_version_ids=version_ids)
