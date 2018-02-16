import logging
from collections import Counter

from peerscout.utils.collection import (
  iter_flatten,
  groupby_to_dict
)

LOGGER = logging.getLogger(__name__)

def create_keyword_map_for_id_keyword_tuples(id_keyword_tuples):
  return groupby_to_dict(id_keyword_tuples, lambda x: x[1].lower(), lambda x: x[0])

def calculate_keyword_scores_using_keyword_map(keyword_map, keyword_list):
  if not keyword_list:
    return {}
  else:
    keyword_count = len(keyword_list)
    return {
      k: v / keyword_count
      for k, v in Counter(iter_flatten(
        keyword_map.get(keyword.lower(), [])
        for keyword in keyword_list
      )).items()
    }

class KeywordService:
  def __init__(self, keyword_map, all_keywords, entity_name='item'):
    self._keyword_map = keyword_map
    self._all_keywords = all_keywords
    self._entity_name = entity_name

  def get_all_keywords(self):
    return self._all_keywords

  def get_keyword_scores(self, keyword_list):
    result = calculate_keyword_scores_using_keyword_map(self._keyword_map, keyword_list)
    LOGGER.debug(
      "found %d %s(s) by keywords: %s", len(result), self._entity_name, keyword_list
    )
    return result
