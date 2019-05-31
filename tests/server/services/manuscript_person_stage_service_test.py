from contextlib import contextmanager

import pytest

import pandas as pd

from peerscout.shared.database import populated_in_memory_database

from peerscout.server.services.manuscript_person_stage_service import (
    ManuscriptPersonStageService,
    StageNames
)

from .test_data import (
    MANUSCRIPT_VERSION1,
    MANUSCRIPT_VERSION_ID1,
    MANUSCRIPT_ID_FIELDS1,
    PERSON_ID1
)

KEYWORD1 = 'keyword1'
KEYWORD2 = 'keyword2'


@contextmanager
def create_manuscript_person_stage_service(dataset) -> ManuscriptPersonStageService:
    with populated_in_memory_database(dataset) as db:
        yield ManuscriptPersonStageService(db)


@pytest.mark.slow
class TestManuscriptPersonStageService:
    class TestGetPersonIdsByVersionIdsForStageNames:
        def test_should_return_empty_dict_if_no_version_ids_are_specified(self):
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
                    service.get_person_ids_by_version_id_for_stage_names(
                        [], [StageNames.REVIEW_RECEIVED]
                    ) == {}
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
                    service.get_person_ids_by_version_id_for_stage_names(
                        [MANUSCRIPT_VERSION_ID1], [StageNames.REVIEW_RECEIVED]
                    ) == {}
                )

        def test_should_return_person_ids_with_matching_stages_by_version_id(self):
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
                    service.get_person_ids_by_version_id_for_stage_names(
                        [MANUSCRIPT_VERSION_ID1], [StageNames.REVIEW_RECEIVED]
                    ) == {
                        MANUSCRIPT_VERSION_ID1: {PERSON_ID1}
                    }
                )
