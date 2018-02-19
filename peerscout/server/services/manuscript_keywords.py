import logging
from collections import Counter

import sqlalchemy

from peerscout.utils.collection import (
  iter_flatten,
  groupby_to_dict
)

from ...shared.database_schema import Person

LOGGER = logging.getLogger(__name__)

def get_person_ids_of_person_keywords_scores(person_keyword_scores):
  return person_keyword_scores.keys()

class ManuscriptKeywordService:
  def __init__(self, db, valid_version_ids=None):
    self._db = db
    self._valid_version_ids = valid_version_ids

  @staticmethod
  def from_database(db, valid_version_ids=None):
    return ManuscriptKeywordService(db, valid_version_ids=valid_version_ids)

  def _query(self, columns):
    db = self._db
    query = db.session.query(*columns)
    if self._valid_version_ids is not None:
      query = query.filter(
        db.manuscript_keyword.table.version_id.in_(self._valid_version_ids)
      )
    return query

  def get_all_keywords(self):
    return set(
      r[0] for r in
      self._query([self._db.manuscript_keyword.table.keyword]).distinct()
    )

  def get_keyword_scores(self, keyword_list):
    if not keyword_list:
      return {}
    num_keywords = len(keyword_list)
    db = self._db
    return dict((keyword, count / num_keywords) for keyword, count in self._query([
      db.manuscript_keyword.table.version_id,
      sqlalchemy.func.count(db.manuscript_keyword.table.version_id)
    ]).filter(
      sqlalchemy.func.lower(db.manuscript_keyword.table.keyword).in_(
        [s.lower() for s in keyword_list]
      )
    ).group_by(db.manuscript_keyword.table.version_id).all())

  def get_keywords_by_ids(self, manuscript_version_ids):
    db = self._db
    return set(
      r[0] for r in
      db.session.query(db.manuscript_keyword.table.keyword)
      .filter(
        sqlalchemy.func.lower(db.manuscript_keyword.table.version_id).in_(
          manuscript_version_ids
        )
      )
      .distinct()
    )
