import logging

from enrichEarlyCareerResearchersInDatabase import (
  extract_manuscript
)

TITLE1 = 'Title 1'
ABSTRACT1 = 'Abstract 1'
MANUSCRIPT_TYPE1 = 'Manuscript Type 1'

def setup_module():
  logging.basicConfig(level=logging.DEBUG)

class TestExtractManuscript(object):
  def test_should_extract_title_if_present(self):
    result = extract_manuscript({
      'title': [TITLE1]
    })
    assert result.get('title') == TITLE1

  def test_should_extract_abstract_if_present(self):
    result = extract_manuscript({
      'abstract': ABSTRACT1
    })
    assert result.get('abstract') == ABSTRACT1

  def test_should_return_none_abstract_if_not_present(self):
    result = extract_manuscript({})
    assert result.get('abstract') is None

  def test_should_extract_type_if_present(self):
    result = extract_manuscript({
      'type': MANUSCRIPT_TYPE1
    })
    assert result.get('manuscript_type') == MANUSCRIPT_TYPE1
