from configparser import ConfigParser

from ...utils.config import dict_to_config

from .search_config import parse_search_config, SEARCH_SECTION_PREFIX, DEFAULT_SEARCH_TYPE

SEARCH_TYPE_1 = 'reviewer'
SEARCH_TYPE_2 = 'editor'
PARAM_KEY_1 = 'param1'
PARAM_VALUE_1 = 'value1'
PARAM_VALUE_2 = 'value2'

def _search_section_name(search_type):
  return SEARCH_SECTION_PREFIX + search_type

class TestParseSearchConfig:
  def test_should_parse_single_search_config(self):
    config = dict_to_config({
      _search_section_name(SEARCH_TYPE_1): {
        PARAM_KEY_1: PARAM_VALUE_1
      }
    })
    search_config = parse_search_config(config)
    assert search_config.keys() == {SEARCH_TYPE_1}
    assert search_config[SEARCH_TYPE_1][PARAM_KEY_1] == PARAM_VALUE_1

  def test_should_parse_multiple_search_configs(self):
    config = dict_to_config({
      _search_section_name(SEARCH_TYPE_1): {
        PARAM_KEY_1: PARAM_VALUE_1
      },
      _search_section_name(SEARCH_TYPE_2): {
        PARAM_KEY_1: PARAM_VALUE_2
      }
    })
    search_config = parse_search_config(config)
    assert search_config.keys() == {SEARCH_TYPE_1, SEARCH_TYPE_2}
    assert search_config[SEARCH_TYPE_1][PARAM_KEY_1] == PARAM_VALUE_1
    assert search_config[SEARCH_TYPE_2][PARAM_KEY_1] == PARAM_VALUE_2

  def test_should_fallback_to_model_config(self):
    config = dict_to_config({
      'model': {
        PARAM_KEY_1: PARAM_VALUE_1
      }
    })
    search_config = parse_search_config(config)
    assert search_config.keys() == {DEFAULT_SEARCH_TYPE}
    assert search_config[SEARCH_TYPE_1][PARAM_KEY_1] == PARAM_VALUE_1

  def test_should_fallback_to_empty_config_if_no_model_config_is_present(self):
    config = dict_to_config({})
    search_config = parse_search_config(config)
    assert search_config.keys() == {DEFAULT_SEARCH_TYPE}
