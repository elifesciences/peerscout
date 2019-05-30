from contextlib import contextmanager

import pytest

from ...shared.database import populated_in_memory_database

from .test_data import (
    MANUSCRIPT_VERSION1,
    MANUSCRIPT_VERSION_ID1,
    MANUSCRIPT_ID_FIELDS1,
    PERSON_ID1, PERSON_ID2
)

from .manuscript_person_relationship_service import (
    ManuscriptPersonRelationshipService,
    RelationshipTypes,
    TABLE_NAME_BY_RELATIONSHIP_TYPE
)

KEYWORD1 = 'keyword1'
KEYWORD2 = 'keyword2'

REGULAR_RELATIONSHIP_TYPES = sorted(
    TABLE_NAME_BY_RELATIONSHIP_TYPE.keys() - {RelationshipTypes.CORRESPONDING_AUTHOR}
)


@contextmanager
def create_manuscript_person_relationship_service(dataset) -> ManuscriptPersonRelationshipService:
    with populated_in_memory_database(dataset) as db:
        yield ManuscriptPersonRelationshipService(db)


@pytest.mark.slow
class TestManuscriptPersonRelationshipService:
    class TestGetPersonIdsByVersionIdsForRelationshipTypes:
        def test_should_return_empty_dict_if_no_version_ids_are_specified(self):
            dataset = {
                'manuscript_version': [MANUSCRIPT_VERSION1],
                'manuscript_author': [{**MANUSCRIPT_ID_FIELDS1, 'person_id': PERSON_ID1}]
            }
            with create_manuscript_person_relationship_service(dataset) as service:
                assert (
                    service.get_person_ids_by_version_id_for_relationship_types(
                        [], [RelationshipTypes.AUTHOR]
                    ) == {}
                )

        @pytest.mark.parametrize('relationship_type', REGULAR_RELATIONSHIP_TYPES)
        def test_should_return_person_ids_for_individual_relationship_types(
                self, relationship_type):
            dataset = {
                'manuscript_version': [MANUSCRIPT_VERSION1],
                TABLE_NAME_BY_RELATIONSHIP_TYPE[relationship_type]: [
                    {**MANUSCRIPT_ID_FIELDS1, 'person_id': PERSON_ID1}
                ]
            }
            with create_manuscript_person_relationship_service(dataset) as service:
                assert (
                    service.get_person_ids_by_version_id_for_relationship_types(
                        [MANUSCRIPT_VERSION_ID1], [relationship_type]
                    ) == {MANUSCRIPT_VERSION_ID1: {PERSON_ID1}}
                )

        def test_should_return_person_ids_for_all_relationship_types(self):
            relationship_types = REGULAR_RELATIONSHIP_TYPES
            person_ids_by_relationship_type = {x: 'p_%s' % x for x in relationship_types}
            dataset = {
                'manuscript_version': [MANUSCRIPT_VERSION1],
                **{
                    TABLE_NAME_BY_RELATIONSHIP_TYPE[relationship_type]: [{
                        **MANUSCRIPT_ID_FIELDS1,
                        'person_id': person_ids_by_relationship_type[relationship_type]
                    }]
                    for relationship_type in relationship_types
                }
            }
            with create_manuscript_person_relationship_service(dataset) as service:
                assert (
                    service.get_person_ids_by_version_id_for_relationship_types(
                        [MANUSCRIPT_VERSION_ID1], relationship_types
                    ) == {MANUSCRIPT_VERSION_ID1: set(person_ids_by_relationship_type.values())}
                )

    class TestGetVersionIdsByPersonIdAndRelationshipType:
        def test_should_return_empty_dict_if_no_person_ids_are_specified(self):
            dataset = {
                'manuscript_version': [MANUSCRIPT_VERSION1],
                'manuscript_author': [{**MANUSCRIPT_ID_FIELDS1, 'person_id': PERSON_ID1}]
            }
            with create_manuscript_person_relationship_service(dataset) as service:
                assert (
                    service.get_version_ids_by_person_id_and_relationship_type(
                        [], [RelationshipTypes.AUTHOR]
                    ) == {}
                )

        @pytest.mark.parametrize('relationship_type', REGULAR_RELATIONSHIP_TYPES)
        def test_should_return_person_ids_for_individual_relationship_types(
                self, relationship_type):
            dataset = {
                'manuscript_version': [MANUSCRIPT_VERSION1],
                TABLE_NAME_BY_RELATIONSHIP_TYPE[relationship_type]: [
                    {**MANUSCRIPT_ID_FIELDS1, 'person_id': PERSON_ID1}
                ]
            }
            with create_manuscript_person_relationship_service(dataset) as service:
                assert (
                    service.get_version_ids_by_person_id_and_relationship_type(
                        [PERSON_ID1], [relationship_type]
                    ) == {
                        PERSON_ID1: {
                            relationship_type: {MANUSCRIPT_VERSION_ID1}
                        }
                    }
                )

        def test_should_return_corresponding_author_person_ids(self):
            dataset = {
                'manuscript_version': [MANUSCRIPT_VERSION1],
                'manuscript_author': [
                    {
                        **MANUSCRIPT_ID_FIELDS1,
                        'person_id': PERSON_ID1,
                        'is_corresponding_author': False
                    },
                    {
                        **MANUSCRIPT_ID_FIELDS1,
                        'person_id': PERSON_ID2,
                        'is_corresponding_author': True
                    }
                ]
            }
            with create_manuscript_person_relationship_service(dataset) as service:
                assert (
                    service.get_version_ids_by_person_id_and_relationship_type(
                        [PERSON_ID1, PERSON_ID2], [RelationshipTypes.CORRESPONDING_AUTHOR]
                    ) == {
                        PERSON_ID2: {
                            RelationshipTypes.CORRESPONDING_AUTHOR: {MANUSCRIPT_VERSION_ID1}
                        }
                    }
                )
