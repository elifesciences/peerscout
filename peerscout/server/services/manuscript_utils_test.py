import logging

from .manuscript_utils import (
  duplicate_manuscript_titles_as_alternatives
)

MANUSCRIPT_ID = 'manuscript_id'
TITLE = 'title'
ABSTRACT = 'abstract'
ALTERNATIVES = 'alternatives'

ABSTRACT_1 = 'Abstract 1'

MANUSCRIPT_1 = {
  MANUSCRIPT_ID: 'manuscript1',
  TITLE: 'Title 1'
}

MANUSCRIPT_2 = {
  MANUSCRIPT_ID: 'manuscript2',
  TITLE: 'Title 2'
}

def get_logger():
  return logging.getLogger(__name__)

def setup_module():
  logging.basicConfig(level='DEBUG')

def sorted_manuscripts(manuscripts):
  return sorted(manuscripts, key=lambda m: m[MANUSCRIPT_ID])

class TestDuplicateManuscriptTitlesAsAlternatives(object):
  def test_should_not_fail_on_empty_list(self):
    assert duplicate_manuscript_titles_as_alternatives([]) == []

  def test_should_not_fail_on_none(self):
    assert duplicate_manuscript_titles_as_alternatives(None) is None

  def test_should_keep_manuscripts_with_different_titles(self):
    manuscripts = [MANUSCRIPT_1, MANUSCRIPT_2]
    result = duplicate_manuscript_titles_as_alternatives(list(manuscripts))
    get_logger().debug('result: %s', result)
    assert sorted_manuscripts(result) == sorted_manuscripts(manuscripts)

  def test_should_not_fail_if_title_is_missing(self):
    manuscripts = [
      MANUSCRIPT_1,
      {
        **MANUSCRIPT_2
      }
    ]
    del manuscripts[1]['title']
    result = duplicate_manuscript_titles_as_alternatives(list(manuscripts))
    get_logger().debug('result: %s', result)
    assert sorted_manuscripts(result) == sorted_manuscripts(manuscripts)

  def test_should_include_duplicate_title_as_alternative(self):
    manuscript_with_same_title = {
      **MANUSCRIPT_2,
      TITLE: MANUSCRIPT_1[TITLE]
    }
    manuscripts = [
      MANUSCRIPT_1,
      manuscript_with_same_title
    ]
    result = duplicate_manuscript_titles_as_alternatives(list(manuscripts))
    get_logger().debug('result: %s', result)
    assert [m[MANUSCRIPT_ID] for m in result] == [MANUSCRIPT_1[MANUSCRIPT_ID]]
    assert result[0][ALTERNATIVES] == [manuscript_with_same_title]

  def test_should_prefer_manuscript_with_abstract(self):
    manuscripts = [
      {
        **MANUSCRIPT_1,
        ABSTRACT: None
      },
      {
        **MANUSCRIPT_2,
        TITLE: MANUSCRIPT_1[TITLE],
        ABSTRACT: ABSTRACT_1
      }
    ]
    result = duplicate_manuscript_titles_as_alternatives(list(manuscripts))
    assert [m[MANUSCRIPT_ID] for m in result] == [MANUSCRIPT_2[MANUSCRIPT_ID]]
