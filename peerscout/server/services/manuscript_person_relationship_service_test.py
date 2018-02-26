from contextlib import contextmanager

import pytest

from ...shared.database import populated_in_memory_database

from .test_data import (
  MANUSCRIPT_VERSION1,
  MANUSCRIPT_VERSION_ID1, MANUSCRIPT_ID_FIELDS2,
  MANUSCRIPT_ID_FIELDS1,
  PERSON_ID1
)

from .manuscript_person_relationship_service import (
  ManuscriptPersonRelationshipService,
  RelationshipTypes,
  TABLE_NAME_BY_RELATIONSHIP_TYPE
)

KEYWORD1 = 'keyword1'
KEYWORD2 = 'keyword2'

@contextmanager
def create_manuscript_person_relationship_service(dataset) -> ManuscriptPersonRelationshipService:
  with populated_in_memory_database(dataset) as db:
    yield ManuscriptPersonRelationshipService(db)

@pytest.mark.slow
class TestManuscriptPersonRelationshipService:
  class TestGetPersonIdsForVersionIdsAndRelationshipType:
    def test_should_return_empty_set_if_no_version_ids_are_specified(self):
      dataset = {
        'manuscript_version': [MANUSCRIPT_VERSION1],
        'manuscript_author': [{**MANUSCRIPT_ID_FIELDS1, 'person_id': PERSON_ID1}]
      }
      with create_manuscript_person_relationship_service(dataset) as service:
        assert (
          service.get_person_ids_for_version_ids_and_relationship_type(
            [], RelationshipTypes.AUTHOR
          ) == set()
        )

    @pytest.mark.parametrize('relationship_type', sorted(TABLE_NAME_BY_RELATIONSHIP_TYPE.keys()))
    def test_should_return_person_ids_for_relationship_types(self, relationship_type):
      dataset = {
        'manuscript_version': [MANUSCRIPT_VERSION1],
        TABLE_NAME_BY_RELATIONSHIP_TYPE[relationship_type]: [
          {**MANUSCRIPT_ID_FIELDS1, 'person_id': PERSON_ID1}
        ]
      }
      with create_manuscript_person_relationship_service(dataset) as service:
        assert (
          service.get_person_ids_for_version_ids_and_relationship_type(
            [MANUSCRIPT_VERSION_ID1], relationship_type
          ) == set([PERSON_ID1])
        )

  class TestGetPersonIdsForVersionIdsAndRelationshipTypes:
    def test_should_return_empty_set_if_no_version_ids_are_specified(self):
      dataset = {
        'manuscript_version': [MANUSCRIPT_VERSION1],
        'manuscript_author': [{**MANUSCRIPT_ID_FIELDS1, 'person_id': PERSON_ID1}]
      }
      with create_manuscript_person_relationship_service(dataset) as service:
        assert (
          service.get_person_ids_for_version_ids_and_relationship_types(
            [], [RelationshipTypes.AUTHOR]
          ) == set()
        )

    @pytest.mark.parametrize('relationship_type', sorted(TABLE_NAME_BY_RELATIONSHIP_TYPE.keys()))
    def test_should_return_person_ids_for_individual_relationship_types(self, relationship_type):
      dataset = {
        'manuscript_version': [MANUSCRIPT_VERSION1],
        TABLE_NAME_BY_RELATIONSHIP_TYPE[relationship_type]: [
          {**MANUSCRIPT_ID_FIELDS1, 'person_id': PERSON_ID1}
        ]
      }
      with create_manuscript_person_relationship_service(dataset) as service:
        assert (
          service.get_person_ids_for_version_ids_and_relationship_types(
            [MANUSCRIPT_VERSION_ID1], [relationship_type]
          ) == set([PERSON_ID1])
        )
