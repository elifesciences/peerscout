from contextlib import contextmanager

import pytest

from ...shared.database import populated_in_memory_database
from ...shared.database_schema import Person

from .test_data import (
    PERSON_ID,
    PERSON_ID1,
    PERSON1
)

from .person_keywords import (
    PersonKeywordService,
    get_person_ids_of_person_keywords_scores
)

KEYWORD1 = 'keyword1'
KEYWORD2 = 'keyword2'


@contextmanager
def create_person_keyword_service(dataset):
    with populated_in_memory_database(dataset) as db:
        yield PersonKeywordService.from_database(db)


@pytest.mark.slow
class TestPersonKeywordService:
    class TestGetKeywordsScores:
        def test_should_return_empty_dict_if_no_keywords_were_specified(self):
            dataset = {
                'person': [PERSON1],
                'person_keyword': [{PERSON_ID: PERSON_ID1, 'keyword': KEYWORD1}]
            }
            with create_person_keyword_service(dataset) as person_keyword_service:
                assert (
                    person_keyword_service.get_keyword_scores([]) ==
                    {}
                )

        def test_should_not_include_persons_with_no_matching_keywords(self):
            dataset = {
                'person': [PERSON1],
                'person_keyword': [{PERSON_ID: PERSON_ID1, 'keyword': KEYWORD1}]
            }
            with create_person_keyword_service(dataset) as person_keyword_service:
                assert (
                    person_keyword_service.get_keyword_scores([KEYWORD2]) ==
                    {}
                )

        def test_should_matching_keyword_case_insensitve(self):
            dataset = {
                'person': [PERSON1],
                'person_keyword': [{PERSON_ID: PERSON_ID1, 'keyword': 'MixedCase'}]
            }
            with create_person_keyword_service(dataset) as person_keyword_service:
                assert (
                    person_keyword_service.get_keyword_scores(['mIXEDcASE']) ==
                    {PERSON_ID1: 1.0}
                )

        def test_should_not_match_inactive_persons(self):
            dataset = {
                'person': [{**PERSON1, 'status': Person.Status.INACTIVE}],
                'person_keyword': [{PERSON_ID: PERSON_ID1, 'keyword': KEYWORD1}]
            }
            with create_person_keyword_service(dataset) as person_keyword_service:
                assert (
                    person_keyword_service.get_keyword_scores([KEYWORD1]) ==
                    {}
                )

        def test_should_calculate_score_for_patially_matching_keywords(self):
            dataset = {
                'person': [PERSON1],
                'person_keyword': [{PERSON_ID: PERSON_ID1, 'keyword': KEYWORD1}]
            }
            with create_person_keyword_service(dataset) as person_keyword_service:
                assert (
                    person_keyword_service.get_keyword_scores([KEYWORD1, KEYWORD2]) ==
                    {PERSON_ID1: 0.5}
                )

        def test_should_calculate_score_for_multiple_matching_keywords(self):
            dataset = {
                'person': [PERSON1],
                'person_keyword': [
                    {PERSON_ID: PERSON_ID1, 'keyword': KEYWORD1},
                    {PERSON_ID: PERSON_ID1, 'keyword': KEYWORD2}
                ]
            }
            with create_person_keyword_service(dataset) as person_keyword_service:
                assert (
                    person_keyword_service.get_keyword_scores([KEYWORD1, KEYWORD2]) ==
                    {PERSON_ID1: 1.0}
                )

    class TestGetAllKeywords:
        def test_should_return_keywords_in_original_case(self):
            dataset = {
                'person': [PERSON1],
                'person_keyword': [
                    {PERSON_ID: PERSON_ID1, 'keyword': KEYWORD1.lower()},
                    {PERSON_ID: PERSON_ID1, 'keyword': KEYWORD2.upper()}
                ]
            }
            with create_person_keyword_service(dataset) as person_keyword_service:
                assert (
                    set(person_keyword_service.get_all_keywords()) ==
                    {KEYWORD1.lower(), KEYWORD2.upper()}
                )

        def test_should_not_include_keywords_of_inactive_persons(self):
            dataset = {
                'person': [{**PERSON1, 'status': Person.Status.INACTIVE}],
                'person_keyword': [{PERSON_ID: PERSON_ID1, 'keyword': KEYWORD1}]
            }
            with create_person_keyword_service(dataset) as person_keyword_service:
                assert (
                    set(person_keyword_service.get_all_keywords()) ==
                    set()
                )


class TestGetPersonIdsOfPersonKeywordsScores:
    def test_should_return_keys(self):
        assert get_person_ids_of_person_keywords_scores({PERSON_ID1: 1.0}) == {PERSON_ID1}
