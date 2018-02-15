import logging
from collections import Counter

from peerscout.utils.collection import (
  iter_flatten,
  groupby_to_dict
)

from ...shared.database_schema import Person

LOGGER = logging.getLogger(__name__)

def get_person_ids_of_person_keywords_scores(person_keyword_scores):
  return person_keyword_scores.keys()

class PersonKeywordService:
  def __init__(self, person_ids_by_keyword_map, all_keywords):
    self._person_ids_by_keyword_map = person_ids_by_keyword_map
    self._all_keywords = all_keywords

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
      person_ids_by_keyword_map=groupby_to_dict(
        person_id_keyword_tuples,
        lambda x: x[1].lower(),
        lambda x: x[0]
      ),
      all_keywords=set(keyword for _, keyword in person_id_keyword_tuples)
    )

  def get_all_keywords(self):
    return self._all_keywords

  def get_person_keywords_scores(self, keyword_list):
    if not keyword_list:
      result = {}
    else:
      keyword_count = len(keyword_list)
      result = {
        k: v / keyword_count
        for k, v in Counter(iter_flatten(
          self._person_ids_by_keyword_map.get(keyword.lower(), [])
          for keyword in keyword_list
        )).items()
      }
    LOGGER.debug(
      "found %d persons by keywords: %s", len(result), keyword_list
    )
    return result
