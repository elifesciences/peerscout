from contextlib import contextmanager

import pytest

from ...shared.database import populated_in_memory_database

from .test_data import (
  MANUSCRIPT_VERSION1,
  MANUSCRIPT_VERSION_ID1,
  MANUSCRIPT_ID_FIELDS1
)

from .manuscript_keywords import (
  ManuscriptKeywordService
)

KEYWORD1 = 'keyword1'
KEYWORD2 = 'keyword2'

@contextmanager
def create_manuscript_keyword_service(dataset, valid_version_ids=None):
  with populated_in_memory_database(dataset) as db:
    yield ManuscriptKeywordService.from_database(db, valid_version_ids=valid_version_ids)

@pytest.mark.slow
class TestManuscriptKeywordService:
  class TestGetKeywordsScores:
    def test_should_return_empty_dict_if_no_keywords_were_specified(self):
      dataset = {
        'manuscript_version': [MANUSCRIPT_VERSION1],
        'manuscript_keyword': [{**MANUSCRIPT_ID_FIELDS1, 'keyword': KEYWORD1}]
      }
      with create_manuscript_keyword_service(dataset) as manuscript_keyword_service:
        assert (
          manuscript_keyword_service.get_keyword_scores([]) ==
          {}
        )

    def test_should_not_include_persons_with_no_matching_keywords(self):
      dataset = {
        'manuscript_version': [MANUSCRIPT_VERSION1],
        'manuscript_keyword': [{**MANUSCRIPT_ID_FIELDS1, 'keyword': KEYWORD1}]
      }
      with create_manuscript_keyword_service(dataset) as manuscript_keyword_service:
        assert (
          manuscript_keyword_service.get_keyword_scores([KEYWORD2]) ==
          {}
        )

    def test_should_matching_keyword_case_insensitve(self):
      dataset = {
        'manuscript_version': [MANUSCRIPT_VERSION1],
        'manuscript_keyword': [{**MANUSCRIPT_ID_FIELDS1, 'keyword': 'MixedCase'}]
      }
      with create_manuscript_keyword_service(dataset) as manuscript_keyword_service:
        assert (
          manuscript_keyword_service.get_keyword_scores(['mIXEDcASE']) ==
          {MANUSCRIPT_VERSION_ID1: 1.0}
        )

    def test_should_match_valid_manuscript(self):
      dataset = {
        'manuscript_version': [MANUSCRIPT_VERSION1],
        'manuscript_keyword': [{**MANUSCRIPT_ID_FIELDS1, 'keyword': KEYWORD1}]
      }
      with create_manuscript_keyword_service(
        dataset, valid_version_ids=[MANUSCRIPT_VERSION_ID1]
      ) as manuscript_keyword_service:
        assert (
          manuscript_keyword_service.get_keyword_scores([KEYWORD1]) ==
          {MANUSCRIPT_VERSION_ID1: 1.0}
        )

    def test_should_not_match_invalid_manuscripts(self):
      dataset = {
        'manuscript_version': [MANUSCRIPT_VERSION1],
        'manuscript_keyword': [{**MANUSCRIPT_ID_FIELDS1, 'keyword': KEYWORD1}]
      }
      with create_manuscript_keyword_service(
        dataset, valid_version_ids=['other']
      ) as manuscript_keyword_service:
        assert (
          manuscript_keyword_service.get_keyword_scores([KEYWORD1]) ==
          {}
        )

    def test_should_calculate_score_for_patially_matching_keywords(self):
      dataset = {
        'manuscript_version': [MANUSCRIPT_VERSION1],
        'manuscript_keyword': [{**MANUSCRIPT_ID_FIELDS1, 'keyword': KEYWORD1}]
      }
      with create_manuscript_keyword_service(dataset) as manuscript_keyword_service:
        assert (
          manuscript_keyword_service.get_keyword_scores([KEYWORD1, KEYWORD2]) ==
          {MANUSCRIPT_VERSION_ID1: 0.5}
        )

    def test_should_calculate_score_for_multiple_matching_keywords(self):
      dataset = {
        'manuscript_version': [MANUSCRIPT_VERSION1],
        'manuscript_keyword': [
          {**MANUSCRIPT_ID_FIELDS1, 'keyword': KEYWORD1},
          {**MANUSCRIPT_ID_FIELDS1, 'keyword': KEYWORD2}
        ]
      }
      with create_manuscript_keyword_service(dataset) as manuscript_keyword_service:
        assert (
          manuscript_keyword_service.get_keyword_scores([KEYWORD1, KEYWORD2]) ==
          {MANUSCRIPT_VERSION_ID1: 1.0}
        )

  class TestGetAllKeywords:
    def test_should_return_keywords_in_original_case(self):
      dataset = {
        'manuscript_version': [MANUSCRIPT_VERSION1],
        'manuscript_keyword': [
          {**MANUSCRIPT_ID_FIELDS1, 'keyword': KEYWORD1.lower()},
          {**MANUSCRIPT_ID_FIELDS1, 'keyword': KEYWORD2.upper()}
        ]
      }
      with create_manuscript_keyword_service(dataset) as manuscript_keyword_service:
        assert (
          set(manuscript_keyword_service.get_all_keywords()) ==
          {KEYWORD1.lower(), KEYWORD2.upper()}
        )

    def test_should_not_include_keywords_of_invalid_manuscripts(self):
      dataset = {
        'manuscript_version': [MANUSCRIPT_VERSION1],
        'manuscript_keyword': [{**MANUSCRIPT_ID_FIELDS1, 'keyword': KEYWORD1}]
      }
      with create_manuscript_keyword_service(
        dataset, valid_version_ids=['other']
      ) as manuscript_keyword_service:
        assert (
          set(manuscript_keyword_service.get_all_keywords()) ==
          set()
        )
