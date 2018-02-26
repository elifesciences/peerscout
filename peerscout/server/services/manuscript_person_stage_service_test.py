from contextlib import contextmanager

import pytest

import pandas as pd

from ...shared.database import populated_in_memory_database

from .test_data import (
  MANUSCRIPT_VERSION1,
  MANUSCRIPT_VERSION_ID1, MANUSCRIPT_ID_FIELDS2,
  MANUSCRIPT_ID_FIELDS1,
  PERSON_ID1
)

from .manuscript_person_stage_service import (
  ManuscriptPersonStageService,
  StageNames
)

KEYWORD1 = 'keyword1'
KEYWORD2 = 'keyword2'

@contextmanager
def create_manuscript_person_stage_service(dataset) -> ManuscriptPersonStageService:
  with populated_in_memory_database(dataset) as db:
    yield ManuscriptPersonStageService(db)

@pytest.mark.slow
class TestManuscriptPersonStageService:
  class TestGetPersonIdsForVersionIdsAndStageNames:
    def test_should_return_empty_set_if_no_version_ids_are_specified(self):
      dataset = {
        'manuscript_version': [MANUSCRIPT_VERSION1],
        'manuscript_stage': [{
          **MANUSCRIPT_ID_FIELDS1, 'person_id': PERSON_ID1,
          'stage_timestamp': pd.Timestamp('2017-01-01'),
          'stage_name': StageNames.REVIEW_RECEIVED
        }]
      }
      with create_manuscript_person_stage_service(dataset) as service:
        assert (
          service.get_person_ids_for_version_ids_and_stage_names(
            [], [StageNames.REVIEW_RECEIVED]
          ) == set()
        )

    def test_should_return_empty_set_if_stage_does_not_match(self):
      dataset = {
        'manuscript_version': [MANUSCRIPT_VERSION1],
        'manuscript_stage': [{
          **MANUSCRIPT_ID_FIELDS1, 'person_id': PERSON_ID1,
          'stage_timestamp': pd.Timestamp('2017-01-01'),
          'stage_name': 'other'
        }]
      }
      with create_manuscript_person_stage_service(dataset) as service:
        assert (
          service.get_person_ids_for_version_ids_and_stage_names(
            [MANUSCRIPT_VERSION_ID1], [StageNames.REVIEW_RECEIVED]
          ) == set()
        )

    def test_should_return_person_ids_with_matching_stages(self):
      dataset = {
        'manuscript_version': [MANUSCRIPT_VERSION1],
        'manuscript_stage': [{
          **MANUSCRIPT_ID_FIELDS1, 'person_id': PERSON_ID1,
          'stage_timestamp': pd.Timestamp('2017-01-01'),
          'stage_name': StageNames.REVIEW_RECEIVED
        }]
      }
      with create_manuscript_person_stage_service(dataset) as service:
        assert (
          service.get_person_ids_for_version_ids_and_stage_names(
            [MANUSCRIPT_VERSION_ID1], [StageNames.REVIEW_RECEIVED]
          ) == {PERSON_ID1}
        )
