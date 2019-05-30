from contextlib import contextmanager

import pytest

from ...shared.database import populated_in_memory_database
from ...shared.database_schema import Person

from .test_data import (
    PERSON_ID,
    PERSON_ID1, PERSON_ID2,
    PERSON1
)

from .person_roles import (
    PersonRoleService
)

EMAIL_1 = 'email1'
EMAIL_2 = 'email2'
ROLE_1 = 'role1'
ROLE_2 = 'role2'


@contextmanager
def create_person_role_service(dataset):
    with populated_in_memory_database(dataset) as db:
        yield PersonRoleService.from_database(db)


@pytest.mark.slow
class TestPersonRoleService:
    class TestFilterPersonIdsByRole:
        def test_should_not_filter_if_role_is_none(self):
            dataset = {}
            with create_person_role_service(dataset) as person_role_service:
                assert (
                    person_role_service.filter_person_ids_by_role({PERSON_ID1}, None) ==
                    {PERSON_ID1}
                )

        def test_should_include_person_with_specified_role(self):
            dataset = {
                'person': [PERSON1],
                'person_role': [{PERSON_ID: PERSON_ID1, 'role': ROLE_1}]
            }
            with create_person_role_service(dataset) as person_role_service:
                assert (
                    person_role_service.filter_person_ids_by_role({PERSON_ID1}, ROLE_1) ==
                    {PERSON_ID1}
                )

        def test_should_not_include_other_persons(self):
            dataset = {
                'person': [PERSON1],
                'person_role': [{PERSON_ID: PERSON_ID2, 'role': ROLE_1}]
            }
            with create_person_role_service(dataset) as person_role_service:
                assert (
                    person_role_service.filter_person_ids_by_role({PERSON_ID1}, ROLE_1) ==
                    set()
                )

        def test_should_not_include_person_with_other_role(self):
            dataset = {
                'person': [PERSON1],
                'person_role': [{PERSON_ID: PERSON_ID1, 'role': ROLE_2}]
            }
            with create_person_role_service(dataset) as person_role_service:
                assert (
                    person_role_service.filter_person_ids_by_role({PERSON_ID1}, ROLE_1) ==
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
                    person_role_service.filter_person_ids_by_role({PERSON_ID1}, ROLE_1) ==
                    {PERSON_ID1}
                )

        def test_should_not_include_inactive_person(self):
            dataset = {
                'person': [{**PERSON1, 'status': Person.Status.INACTIVE}],
                'person_role': [{PERSON_ID: PERSON_ID1, 'role': ROLE_1}]
            }
            with create_person_role_service(dataset) as person_role_service:
                assert (
                    person_role_service.filter_person_ids_by_role({PERSON_ID1}, ROLE_1) ==
                    set()
                )

    class TestUserHasRoleByEmail:
        def test_should_return_whether_user_has_role(self):
            dataset = {
                'person': [{**PERSON1, 'email': EMAIL_1}],
                'person_role': [{PERSON_ID: PERSON_ID1, 'role': ROLE_1}]
            }
            with create_person_role_service(dataset) as person_role_service:
                assert person_role_service.user_has_role_by_email(
                    email=EMAIL_1, role=ROLE_1) is True
                assert person_role_service.user_has_role_by_email(
                    email=EMAIL_1, role='other') is False
                assert person_role_service.user_has_role_by_email(
                    email='other', role=ROLE_1) is False

    class TestGetUserRolesByEmail:
        def test_should_return_roles_of_existing_user(self):
            dataset = {
                'person': [{**PERSON1, 'email': EMAIL_1}],
                'person_role': [
                    {PERSON_ID: PERSON_ID1, 'role': ROLE_1},
                    {PERSON_ID: PERSON_ID1, 'role': ROLE_2}
                ]
            }
            with create_person_role_service(dataset) as person_role_service:
                assert person_role_service.get_user_roles_by_email(email=EMAIL_1) == {
                    ROLE_1, ROLE_2}

        def test_should_not_return_roles_of_not_matching_user(self):
            dataset = {
                'person': [{**PERSON1, 'email': EMAIL_1}],
                'person_role': [
                    {PERSON_ID: PERSON_ID1, 'role': ROLE_1},
                    {PERSON_ID: PERSON_ID1, 'role': ROLE_2}
                ]
            }
            with create_person_role_service(dataset) as person_role_service:
                assert person_role_service.get_user_roles_by_email(email=EMAIL_2) == set()
