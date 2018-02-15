from contextlib import contextmanager

import pytest

from ...shared.database import populated_in_memory_database
from ...shared.database_schema import Person

from .test_data import (
  PERSON_ID,
  PERSON_ID1,
  PERSON1
)

from .person_roles import (
  PersonRoleService
)

ROLE_1 = 'role1'
ROLE_2 = 'role2'

@contextmanager
def create_person_role_service(dataset):
  with populated_in_memory_database(dataset) as db:
    yield PersonRoleService.from_database(db)

@pytest.mark.slow
class TestPersonRoleService:
  class TestFilterPersonIdsByRole:
    def test_should_include_person_with_specified_role(self):
      dataset = {
        'person': [PERSON1],
        'person_role': [{PERSON_ID: PERSON_ID1, 'role': ROLE_1}]
      }
      with create_person_role_service(dataset) as person_role_service:
        assert (
          person_role_service.filter_person_ids_by_role([PERSON_ID1], ROLE_1) ==
          {PERSON_ID1}
        )

    def test_should_not_include_person_with_other_role(self):
      dataset = {
        'person': [PERSON1],
        'person_role': [{PERSON_ID: PERSON_ID1, 'role': ROLE_2}]
      }
      with create_person_role_service(dataset) as person_role_service:
        assert (
          person_role_service.filter_person_ids_by_role([PERSON_ID1], ROLE_1) ==
          set()
        )

    def test_should_include_person_with_multiple_roles(self):
      dataset = {
        'person': [PERSON1],
        'person_role': [
          {PERSON_ID: PERSON_ID1, 'role': ROLE_1},
          {PERSON_ID: PERSON_ID1, 'role': ROLE_2}
        ]
      }
      with create_person_role_service(dataset) as person_role_service:
        assert (
          person_role_service.filter_person_ids_by_role([PERSON_ID1], ROLE_1) ==
          {PERSON_ID1}
        )

    def test_should_not_include_inactive_person(self):
      dataset = {
        'person': [{**PERSON1, 'status': Person.Status.INACTIVE}],
        'person_role': [{PERSON_ID: PERSON_ID1, 'role': ROLE_1}]
      }
      with create_person_role_service(dataset) as person_role_service:
        assert (
          person_role_service.filter_person_ids_by_role([PERSON_ID1], ROLE_1) ==
          set()
        )
