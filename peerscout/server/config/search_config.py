from typing import Dict
from configparser import ConfigParser

from peerscout.utils.collection import parse_list

SEARCH_SECTION_PREFIX = 'search:'
DEFAULT_SEARCH_TYPE = 'reviewer'

LIST_KEYS = {'recommend_relationship_types', 'recommend_stage_names'}

def parse_search_config(app_config: ConfigParser) -> Dict[str, str]:
  search_config = {
    section[len(SEARCH_SECTION_PREFIX):]: dict(app_config[section])
    for section in app_config.sections()
    if section.startswith(SEARCH_SECTION_PREFIX)
  }
  if not search_config:
    search_config = {
      DEFAULT_SEARCH_TYPE: dict(app_config['model']) if 'model' in app_config else {}
    }
  for search_type in search_config.keys():
    for k in LIST_KEYS:
      if k in search_config[search_type]:
        search_config[search_type][k] = parse_list(search_config[search_type][k])
  return search_config
