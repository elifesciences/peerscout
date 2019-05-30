from contextlib import contextmanager

import pytest

from peerscout.shared.database import populated_in_memory_database

from peerscout.server.services.manuscript_subject_areas import (
    ManuscriptSubjectAreaService
)

from .test_data import (
    MANUSCRIPT_VERSION1,
    MANUSCRIPT_VERSION_ID1,
    MANUSCRIPT_ID_FIELDS1
)

SUBJECT_AREA1 = 'Subject Area 1'
SUBJECT_AREA2 = 'Subject Area 2'


@contextmanager
def create_manuscript_subject_area_service(dataset, valid_version_ids=None):
    with populated_in_memory_database(dataset) as db:
        yield ManuscriptSubjectAreaService.from_database(db, valid_version_ids=valid_version_ids)


@pytest.mark.slow
class TestManuscriptSubjectAreaService:
    class TestGetIdsBySubjectAreas:
        def test_should_return_empty_dict_if_no_subject_areas_were_specified(self):
            dataset = {
                'manuscript_version': [MANUSCRIPT_VERSION1],
                'manuscript_subject_area': [
                    {**MANUSCRIPT_ID_FIELDS1, 'subject_area': SUBJECT_AREA1}
                ]
            }
            with create_manuscript_subject_area_service(dataset) as manuscript_subject_area_service:
                assert (
                    manuscript_subject_area_service.get_ids_by_subject_areas([]) ==
                    set()
                )

        def test_should_not_include_persons_with_no_matching_keywords(self):
            dataset = {
                'manuscript_version': [MANUSCRIPT_VERSION1],
                'manuscript_subject_area': [
                    {**MANUSCRIPT_ID_FIELDS1, 'subject_area': SUBJECT_AREA1}
                ]
            }
            with create_manuscript_subject_area_service(dataset) as manuscript_subject_area_service:
                assert (
                    manuscript_subject_area_service.get_ids_by_subject_areas([SUBJECT_AREA2]) ==
                    set()
                )

        def test_should_matching_keyword_case_insensitve(self):
            dataset = {
                'manuscript_version': [MANUSCRIPT_VERSION1],
                'manuscript_subject_area': [{**MANUSCRIPT_ID_FIELDS1, 'subject_area': 'MixedCase'}]
            }
            with create_manuscript_subject_area_service(dataset) as manuscript_subject_area_service:
                assert (
                    manuscript_subject_area_service.get_ids_by_subject_areas(['mIXEDcASE']) ==
                    {MANUSCRIPT_VERSION_ID1}
                )

        def test_should_match_valid_manuscript(self):
            dataset = {
                'manuscript_version': [MANUSCRIPT_VERSION1],
                'manuscript_subject_area': [
                    {**MANUSCRIPT_ID_FIELDS1, 'subject_area': SUBJECT_AREA1}
                ]
            }
            with create_manuscript_subject_area_service(
                    dataset, valid_version_ids=[MANUSCRIPT_VERSION_ID1]
                ) as manuscript_subject_area_service:
                assert (
                    manuscript_subject_area_service.get_ids_by_subject_areas([SUBJECT_AREA1]) ==
                    {MANUSCRIPT_VERSION_ID1}
                )

        def test_should_not_match_invalid_manuscripts(self):
            dataset = {
                'manuscript_version': [MANUSCRIPT_VERSION1],
                'manuscript_subject_area': [
                    {**MANUSCRIPT_ID_FIELDS1, 'subject_area': SUBJECT_AREA1}
                ]
            }
            with create_manuscript_subject_area_service(
                    dataset, valid_version_ids=['other']
                ) as manuscript_subject_area_service:
                assert (
                    manuscript_subject_area_service.get_ids_by_subject_areas([SUBJECT_AREA1]) ==
                    set()
                )

    class TestGetSubjectAreasById:
        def test_should_return_single_subject_area_of_matching_id(self):
            dataset = {
                'manuscript_version': [MANUSCRIPT_VERSION1],
                'manuscript_subject_area': [
                    {**MANUSCRIPT_ID_FIELDS1, 'subject_area': SUBJECT_AREA1}
                ]
            }
            with create_manuscript_subject_area_service(dataset) as manuscript_subject_area_service:
                assert (
                    set(manuscript_subject_area_service.get_subject_areas_by_id(
                        MANUSCRIPT_VERSION_ID1
                    )) == {SUBJECT_AREA1}
                )

        def test_should_return_multiple_subject_areas_of_matching_id(self):
            dataset = {
                'manuscript_version': [MANUSCRIPT_VERSION1],
                'manuscript_subject_area': [
                    {**MANUSCRIPT_ID_FIELDS1, 'subject_area': SUBJECT_AREA1},
                    {**MANUSCRIPT_ID_FIELDS1, 'subject_area': SUBJECT_AREA2}
                ]
            }
            with create_manuscript_subject_area_service(dataset) as manuscript_subject_area_service:
                assert (
                    set(manuscript_subject_area_service.get_subject_areas_by_id(
                        MANUSCRIPT_VERSION_ID1
                    )) == {SUBJECT_AREA1, SUBJECT_AREA2}
                )

        def test_should_return_empty_list_if_no_subject_areas_are_mapped_to_id(self):
            dataset = {
                'manuscript_version': [MANUSCRIPT_VERSION1]
            }
            with create_manuscript_subject_area_service(dataset) as manuscript_subject_area_service:
                assert (
                    set(manuscript_subject_area_service.get_subject_areas_by_id(
                        MANUSCRIPT_VERSION_ID1
                    )) == set()
                )

    class TestGetAllSubjectAreas:
        def test_should_return_keywords_in_original_case(self):
            dataset = {
                'manuscript_version': [MANUSCRIPT_VERSION1],
                'manuscript_subject_area': [
                    {**MANUSCRIPT_ID_FIELDS1, 'subject_area': SUBJECT_AREA1.lower()},
                    {**MANUSCRIPT_ID_FIELDS1, 'subject_area': SUBJECT_AREA2.upper()}
                ]
            }
            with create_manuscript_subject_area_service(dataset) as manuscript_subject_area_service:
                assert (
                    manuscript_subject_area_service.get_all_subject_areas() ==
                    {SUBJECT_AREA1.lower(), SUBJECT_AREA2.upper()}
                )

        def test_should_not_include_keywords_of_invalid_manuscripts(self):
            dataset = {
                'manuscript_version': [MANUSCRIPT_VERSION1],
                'manuscript_subject_area': [
                    {**MANUSCRIPT_ID_FIELDS1, 'subject_area': SUBJECT_AREA1}
                ]
            }
            with create_manuscript_subject_area_service(
                    dataset, valid_version_ids=['other']
                ) as manuscript_subject_area_service:
                assert (
                    manuscript_subject_area_service.get_all_subject_areas() ==
                    set()
                )
