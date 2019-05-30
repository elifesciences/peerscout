from contextlib import contextmanager
from typing import ContextManager

import pytest

from ...shared.database import populated_in_memory_database, Dataset

from .test_data import (
    MANUSCRIPT_VERSION1,
    MANUSCRIPT_VERSION_ID1,
    Decisions,
    TYPE_RESEARCH_ARTICLE,
    PUBLISHED_DECISIONS,
    PUBLISHED_MANUSCRIPT_TYPES,
    VALID_DECISIONS,
    VALID_MANUSCRIPT_TYPES
)

from .ManuscriptModel import (
    ManuscriptModel
)

VALID_MANUSCRIPT_TYPE = TYPE_RESEARCH_ARTICLE

VALID_MANUSCRIPT_VERSION = {
    **MANUSCRIPT_VERSION1,
    'decision': Decisions.REJECTED,
    'manuscript_type': VALID_MANUSCRIPT_TYPE,
    'is_published': None  # by default infer from decision
}

PUBLISHED_MANUSCRIPT_VERSION = {
    **VALID_MANUSCRIPT_VERSION,
    'decision': Decisions.ACCEPTED
}

NOT_MATCHING_DECISION = 'other decision'
NOT_MATCHING_MANUSCRIPT_TYPE = 'other manuscript type'

EMPTY_DATASET = {}


@contextmanager
def create_manuscript_model(dataset: Dataset) -> ContextManager[ManuscriptModel]:
    with populated_in_memory_database(dataset) as db:
        yield ManuscriptModel(
            db,
            valid_decisions=VALID_DECISIONS,
            valid_manuscript_types=VALID_MANUSCRIPT_TYPES,
            published_decisions=PUBLISHED_DECISIONS,
            published_manuscript_types=PUBLISHED_MANUSCRIPT_TYPES
        )


@pytest.mark.slow
class TestManuscriptModel:
    class TestIsValidManuscript:
        def test_should_return_empty_set_if_there_are_no_manuscripts(self):
            with create_manuscript_model(EMPTY_DATASET) as manuscript_model:
                assert manuscript_model.valid_version_ids == set()

        def test_should_return_manuscript_version_id_with_matching_decision_and_type(self):
            dataset = {
                'manuscript_version': [VALID_MANUSCRIPT_VERSION]
            }
            with create_manuscript_model(dataset) as manuscript_model:
                assert manuscript_model.get_valid_manuscript_version_ids() == {
                    MANUSCRIPT_VERSION_ID1}

        def test_should_not_return_manuscript_version_id_with_not_matching_decision(self):
            manuscript_version = {
                **VALID_MANUSCRIPT_VERSION,
                'decision': NOT_MATCHING_DECISION
            }
            dataset = {
                'manuscript_version': [manuscript_version]
            }
            with create_manuscript_model(dataset) as manuscript_model:
                assert manuscript_model.get_valid_manuscript_version_ids() == set()

        def test_should_return_manuscript_version_id_with_not_matching_decision_but_published(self):
            manuscript_version = {
                **VALID_MANUSCRIPT_VERSION,
                'decision': NOT_MATCHING_DECISION,
                'is_published': True
            }
            dataset = {
                'manuscript_version': [manuscript_version]
            }
            with create_manuscript_model(dataset) as manuscript_model:
                assert manuscript_model.get_valid_manuscript_version_ids() == {
                    MANUSCRIPT_VERSION_ID1}

        def test_should_return_manuscript_version_id_with_none_decision_but_published(self):
            manuscript_version = {
                **VALID_MANUSCRIPT_VERSION,
                'decision': None,
                'is_published': True
            }
            dataset = {
                'manuscript_version': [manuscript_version]
            }
            with create_manuscript_model(dataset) as manuscript_model:
                assert manuscript_model.get_valid_manuscript_version_ids() == {
                    MANUSCRIPT_VERSION_ID1}

        # TODO revise what it means to be valid
        def test_should_return_manuscript_version_id_with_none_decision_and_none_published_flag(
                self):
            manuscript_version = {
                **VALID_MANUSCRIPT_VERSION,
                'decision': None,
                'is_published': None
            }
            dataset = {
                'manuscript_version': [manuscript_version]
            }
            with create_manuscript_model(dataset) as manuscript_model:
                assert manuscript_model.get_valid_manuscript_version_ids() == {
                    MANUSCRIPT_VERSION_ID1}

        def test_should_not_return_manuscript_version_id_with_not_matching_manuscript_type(self):
            manuscript_version = {
                **VALID_MANUSCRIPT_VERSION,
                'manuscript_type': NOT_MATCHING_MANUSCRIPT_TYPE
            }
            dataset = {
                'manuscript_version': [manuscript_version]
            }
            with create_manuscript_model(dataset) as manuscript_model:
                assert manuscript_model.get_valid_manuscript_version_ids() == set()

        def test_should_not_return_manuscript_version_id_with_none_manuscript_type(self):
            manuscript_version = {
                **VALID_MANUSCRIPT_VERSION,
                'manuscript_type': None
            }
            dataset = {
                'manuscript_version': [manuscript_version]
            }
            with create_manuscript_model(dataset) as manuscript_model:
                assert manuscript_model.get_valid_manuscript_version_ids() == set()

    class TestIsPublishedManuscript:
        def test_should_true_for_matching_decision_and_type(self):
            with create_manuscript_model(EMPTY_DATASET) as manuscript_model:
                assert manuscript_model.is_manuscript_published(PUBLISHED_MANUSCRIPT_VERSION)

        def test_should_return_false_for_valid_but_not_published_decision(self):
            manuscript_version = {
                **PUBLISHED_MANUSCRIPT_VERSION,
                'decision': VALID_MANUSCRIPT_VERSION['decision']
            }
            with create_manuscript_model(EMPTY_DATASET) as manuscript_model:
                assert not manuscript_model.is_manuscript_published(manuscript_version)

        def test_should_return_false_for_not_matching_manuscript_type(self):
            manuscript_version = {
                **PUBLISHED_MANUSCRIPT_VERSION,
                'manuscript_type': NOT_MATCHING_MANUSCRIPT_TYPE
            }
            with create_manuscript_model(EMPTY_DATASET) as manuscript_model:
                assert not manuscript_model.is_manuscript_published(manuscript_version)

        def test_should_return_false_for_none_manuscript_type(self):
            manuscript_version = {
                **PUBLISHED_MANUSCRIPT_VERSION,
                'manuscript_type': None
            }
            with create_manuscript_model(EMPTY_DATASET) as manuscript_model:
                assert not manuscript_model.is_manuscript_published(manuscript_version)

        def test_should_return_false_if_decision_is_none(self):
            manuscript_version = {
                **PUBLISHED_MANUSCRIPT_VERSION,
                'decision': None
            }
            with create_manuscript_model(EMPTY_DATASET) as manuscript_model:
                assert not manuscript_model.is_manuscript_published(manuscript_version)

        def test_should_return_false_if_decision_is_none_but_published_flag_is_set(self):
            manuscript_version = {
                **PUBLISHED_MANUSCRIPT_VERSION,
                'decision': None,
                'is_published': True
            }
            with create_manuscript_model(EMPTY_DATASET) as manuscript_model:
                assert manuscript_model.is_manuscript_published(manuscript_version)

        def test_should_return_false_if_decision_is_not_matching_but_published_flag_is_set(self):
            manuscript_version = {
                **PUBLISHED_MANUSCRIPT_VERSION,
                'decision': NOT_MATCHING_DECISION,
                'is_published': True
            }
            with create_manuscript_model(EMPTY_DATASET) as manuscript_model:
                assert manuscript_model.is_manuscript_published(manuscript_version)
