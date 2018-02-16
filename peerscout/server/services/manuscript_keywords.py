import logging
from collections import Counter

from peerscout.utils.collection import (
  iter_flatten,
  groupby_to_dict
)

from ...shared.database_schema import Person

from .keywords import (
  create_keyword_map_for_id_keyword_tuples,
  calculate_keyword_scores_using_keyword_map,
  KeywordService
)

LOGGER = logging.getLogger(__name__)

def get_person_ids_of_person_keywords_scores(person_keyword_scores):
  return person_keyword_scores.keys()

class ManuscriptKeywordService(KeywordService):
  def __init__(self, keyword_map, all_keywords):
    super(ManuscriptKeywordService, self).__init__(
      keyword_map, all_keywords, entity_name='manuscript'
    )

  @staticmethod
  def from_database(db, valid_version_ids=None):
    query = db.session.query(
      db.manuscript_keyword.table.version_id,
      db.manuscript_keyword.table.keyword
    )
    if valid_version_ids is not None:
      query = query.filter(
        db.manuscript_keyword.table.version_id.in_(valid_version_ids)
      )
    return ManuscriptKeywordService.from_manuscript_version_id_keyword_tuples(
      query.all()
    )

  @staticmethod
  def from_manuscript_version_id_keyword_tuples(manuscript_version_id_keyword_tuples):
    return ManuscriptKeywordService(
      keyword_map=create_keyword_map_for_id_keyword_tuples(
        manuscript_version_id_keyword_tuples
      ),
      all_keywords=set(keyword for _, keyword in manuscript_version_id_keyword_tuples)
    )
