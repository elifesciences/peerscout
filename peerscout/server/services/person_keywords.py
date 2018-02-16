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

class PersonKeywordService(KeywordService):
  def __init__(self, keyword_map, all_keywords):
    super(PersonKeywordService, self).__init__(keyword_map, all_keywords, entity_name='person')

  @staticmethod
  def from_database(db):
    return PersonKeywordService.from_person_id_keyword_tuples(
      db.session.query(
        db.person_keyword.table.person_id,
        db.person_keyword.table.keyword
      ).join(
        db.person.table,
        db.person.table.status == Person.Status.ACTIVE
      ).all(),
    )

  @staticmethod
  def from_person_id_keyword_tuples(person_id_keyword_tuples):
    return PersonKeywordService(
      keyword_map=create_keyword_map_for_id_keyword_tuples(person_id_keyword_tuples),
      all_keywords=set(keyword for _, keyword in person_id_keyword_tuples)
    )
