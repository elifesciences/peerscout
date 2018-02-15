import logging
from collections import Counter

from peerscout.utils.collection import (
  iter_flatten,
  groupby_columns_to_dict
)

LOGGER = logging.getLogger(__name__)

def get_person_ids_of_person_keywords_scores(person_keyword_scores):
  return person_keyword_scores.keys()

class PersonKeywordService:
  def __init__(self, person_ids_by_keyword_map, all_keywords):
    self._person_ids_by_keyword_map = person_ids_by_keyword_map
    self._all_keywords = all_keywords

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

  @staticmethod
  def from_database(db):
    return PersonKeywordService.from_dataframe(
      db.person_keyword.read_frame().reset_index()
    )

  @staticmethod
  def from_dataframe(person_keywords_df):
    return PersonKeywordService(
      person_ids_by_keyword_map = groupby_columns_to_dict(
        person_keywords_df['keyword'].str.lower(),
        person_keywords_df['person_id']
      ),
      all_keywords=set(person_keywords_df['keyword'])
    )
