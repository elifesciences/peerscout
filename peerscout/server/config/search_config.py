from typing import Dict
from configparser import ConfigParser

SEARCH_SECTION_PREFIX = 'search:'
DEFAULT_SEARCH_TYPE = 'reviewer'

def parse_search_config(app_config: ConfigParser) -> Dict[str, str]:
  search_config = {
    section[len(SEARCH_SECTION_PREFIX):]: app_config[section]
    for section in app_config.sections()
    if section.startswith(SEARCH_SECTION_PREFIX)
  }
  if not search_config:
    search_config = {
      DEFAULT_SEARCH_TYPE: app_config['model'] if 'model' in app_config else {}
    }
  return search_config
