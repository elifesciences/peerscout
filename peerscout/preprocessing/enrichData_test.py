import logging
import json
from typing import Dict
from unittest.mock import patch, Mock, ANY
from configparser import ConfigParser
from datetime import datetime, timedelta

import pytest

from peerscout.utils.config import dict_to_config

from ..shared.database import populated_in_memory_database

from . import enrichData as enrich_data_module
from .enrichData import (
    extract_manuscript,
    contains_author_with_orcid,
    create_str_cache,
    enrich_and_update_person_list,
    get_crossref_works_by_orcid_url,
    get_crossref_works_by_full_name_url,
    parse_int_list,
    decorate_get_request_handler,
    get_persons_to_enrich,
    main,
    DEFAULT_MAX_WORKERS
)

LOGGER = logging.getLogger(__name__)

URL_1 = 'test://dummy.url'
URL_2 = 'test://dummy.url2'

TITLE1 = 'Title 1'
ABSTRACT1 = 'Abstract 1'
MANUSCRIPT_TYPE1 = 'Manuscript Type 1'

# Schema field names
PERSON_ID = 'person_id'
MANUSCRIPT_ID = 'manuscript_id'
DOI = 'doi'

PERSON_ID_1 = 'person1'
PERSON_ID_2 = 'person2'

FIRST_NAME_1 = 'Jon'
LAST_NAME_1 = 'Smith'

PERSON_1 = {
    PERSON_ID: PERSON_ID_1,
    'first_name': FIRST_NAME_1,
    'last_name': LAST_NAME_1,
    'is_early_career_researcher': False
}

ECR_1 = {
    **PERSON_1,
    'is_early_career_researcher': True
}

ORCID_1 = 'orcid1'

ORCID_MEMBERSHIP_1 = {
    PERSON_ID: PERSON_ID_1,
    'member_type': 'ORCID',
    'member_id': ORCID_1
}

DOI_1 = 'doi1'
DOI_2 = 'doi2'

MANUSCRIPT_ID_1 = 'manuscript1'

ROLE_1 = 'role1'
ROLE_2 = 'role2'

EMPTY_DATASET = {}


def setup_module():
    logging.root.handlers = []
    logging.basicConfig(level=logging.DEBUG)


def get_crossref_response(items):
    return json.dumps({
        'message': {
            'items': items
        }
    })


@pytest.fixture(name='mock_f')
def _mock_f():
    mock_f = Mock()
    mock_f.return_value = 'mock_f return_value'
    return mock_f


class TestCreateStrCache:
    @pytest.fixture
    def now(self):
        with patch.object(enrich_data_module, 'get_current_time') as now:
            yield now

    @pytest.fixture
    def getmtime(self):
        with patch('os.path.getmtime') as getmtime:
            yield getmtime

    def test_should_call_function_and_return_value_if_not_in_cache(self, tmpdir, mock_f: Mock):
        cached_f = create_str_cache(mock_f, str(tmpdir))
        assert cached_f(URL_1) == mock_f.return_value
        mock_f.assert_called_with(URL_1)

    def test_should_call_function_only_once_called_with_the_same_parameter(
            self, tmpdir, mock_f: Mock):

        cached_f = create_str_cache(mock_f, str(tmpdir))
        cached_f(URL_1)
        assert cached_f(URL_1) == mock_f.return_value
        assert mock_f.call_count == 1

    def test_should_call_function_multiple_times_if_called_with_the_different_parameter(
            self, tmpdir, mock_f: Mock):

        cached_f = create_str_cache(mock_f, str(tmpdir))
        cached_f(URL_1)
        assert cached_f(URL_2) == mock_f.return_value
        assert mock_f.call_count == 2
        mock_f.assert_called_with(URL_2)

    def test_should_call_function_twice_if_cache_has_expired(
            self, tmpdir, mock_f: Mock, now: Mock, getmtime: Mock):

        now.return_value = datetime(2018, 1, 1)
        getmtime.return_value = now.return_value.timestamp()

        LOGGER.info('str(tmpdir): %s', str(tmpdir))
        cached_f = create_str_cache(mock_f, str(tmpdir), expire_after_secs=10)
        cached_f(URL_1)

        now.return_value = now.return_value + timedelta(seconds=10)

        assert cached_f(URL_1) == mock_f.return_value
        assert mock_f.call_count == 2

    def test_should_call_function_once_if_cache_has_not_yet_expired(
            self, tmpdir, mock_f: Mock, now: Mock, getmtime: Mock):

        now.return_value = datetime(2018, 1, 1)
        getmtime.return_value = now.return_value.timestamp()

        cached_f = create_str_cache(mock_f, str(tmpdir), expire_after_secs=10)
        cached_f(URL_1)

        now.return_value = now.return_value + timedelta(seconds=9)

        assert cached_f(URL_1) == mock_f.return_value
        assert mock_f.call_count == 1


class TestExtractManuscript:
    def test_should_extract_title_if_present(self):
        result = extract_manuscript({
            'title': [TITLE1]
        })
        assert result.get('title') == TITLE1

    def test_should_extract_abstract_if_present(self):
        result = extract_manuscript({
            'abstract': ABSTRACT1
        })
        assert result.get('abstract') == ABSTRACT1

    def test_should_return_none_abstract_if_not_present(self):
        result = extract_manuscript({})
        assert result.get('abstract') is None

    def test_should_extract_type_if_present(self):
        result = extract_manuscript({
            'type': MANUSCRIPT_TYPE1
        })
        assert result.get('manuscript_type') == MANUSCRIPT_TYPE1


def MapRequestHandler(response_by_url_map: Dict[str, str]):
    def get_request_handler(url):
        response_text = response_by_url_map.get(url)
        if not response_text:
            raise RuntimeError('url not configured: {}'.format(url))
        return response_text
    return get_request_handler


class TestContainsAuthorWithOrcid:
    def test_should_false_if_item_has_no_authors(self):
        assert not contains_author_with_orcid({}, ORCID_1)

    def test_should_false_if_author_does_not_have_orcid(self):
        assert not contains_author_with_orcid({
            'author': {}
        }, ORCID_1)

    def test_should_false_if_orcid_does_not_match(self):
        assert not contains_author_with_orcid({
            'author': [{'ORCID': 'other'}]
        }, ORCID_1)

    def test_should_true_if_orcid_matches(self):
        assert contains_author_with_orcid({
            'author': [{'ORCID': ORCID_1}]
        }, ORCID_1)


class TestGetPersonsToEnrich:
    def test_should_raise_error_if_no_filter_option_specified(self):
        with populated_in_memory_database(EMPTY_DATASET) as db:
            with pytest.raises(AssertionError):
                get_persons_to_enrich(db)

    def test_should_include_ecr_without_orcid_membership(self):
        dataset = {
            'person': [ECR_1]
        }
        with populated_in_memory_database(dataset) as db:
            person_list = get_persons_to_enrich(db, include_early_career_researchers=True)
            assert {p[PERSON_ID] for p in person_list} == {ECR_1[PERSON_ID]}
            assert {p.get('ORCID') for p in person_list} == {None}

    def test_should_include_ecr_with_orcid_membership(self):
        dataset = {
            'person': [ECR_1],
            'person_membership': [ORCID_MEMBERSHIP_1]
        }
        with populated_in_memory_database(dataset) as db:
            person_list = get_persons_to_enrich(db, include_early_career_researchers=True)
            assert {p[PERSON_ID] for p in person_list} == {ECR_1[PERSON_ID]}
            LOGGER.debug('person_list: %s', person_list)
            assert {p.get('ORCID') for p in person_list} == {ORCID_1}

    def test_should_include_person_by_role_without_orcid_membership(self):
        dataset = {
            'person': [PERSON_1],
            'person_role': [{PERSON_ID: PERSON_ID_1, 'role': ROLE_1}]
        }
        with populated_in_memory_database(dataset) as db:
            person_list = get_persons_to_enrich(db, include_roles=[ROLE_1])
            assert {p[PERSON_ID] for p in person_list} == {PERSON_ID_1}
            LOGGER.debug('person_list: %s', person_list)
            assert {p.get('ORCID') for p in person_list} == {None}

    def test_should_include_person_by_role_with_orcid_membership(self):
        dataset = {
            'person': [PERSON_1],
            'person_role': [{PERSON_ID: PERSON_ID_1, 'role': ROLE_1}],
            'person_membership': [ORCID_MEMBERSHIP_1]
        }
        with populated_in_memory_database(dataset) as db:
            person_list = get_persons_to_enrich(db, include_roles=[ROLE_1])
            assert {p[PERSON_ID] for p in person_list} == {PERSON_ID_1}
            LOGGER.debug('person_list: %s', person_list)
            assert {p.get('ORCID') for p in person_list} == {ORCID_1}

    def test_should_not_include_person_with_different_role(self):
        dataset = {
            'person': [PERSON_1],
            'person_role': [{PERSON_ID: PERSON_ID_1, 'role': ROLE_2}]
        }
        with populated_in_memory_database(dataset) as db:
            person_list = get_persons_to_enrich(db, include_roles=[ROLE_1])
            assert {p[PERSON_ID] for p in person_list} == set()

    def test_should_not_include_person_without_a_role(self):
        dataset = {
            'person': [PERSON_1]
        }
        with populated_in_memory_database(dataset) as db:
            person_list = get_persons_to_enrich(db, include_roles=[ROLE_1])
            assert {p[PERSON_ID] for p in person_list} == set()

    def test_should_include_person_by_role_once_with_multiple_matching_roles(self):
        dataset = {
            'person': [PERSON_1],
            'person_role': [
                {PERSON_ID: PERSON_ID_1, 'role': ROLE_1},
                {PERSON_ID: PERSON_ID_1, 'role': ROLE_2}
            ]
        }
        with populated_in_memory_database(dataset) as db:
            person_list = get_persons_to_enrich(db, include_roles=[ROLE_1, ROLE_2])
            assert [p[PERSON_ID] for p in person_list] == [PERSON_ID_1]

    def test_should_include_person_by_ecr_and_role(self):
        dataset = {
            'person': [
                {**PERSON_1, PERSON_ID: PERSON_ID_1},
                {**ECR_1, PERSON_ID: PERSON_ID_2}
            ],
            'person_role': [{PERSON_ID: PERSON_ID_1, 'role': ROLE_1}]
        }
        with populated_in_memory_database(dataset) as db:
            person_list = get_persons_to_enrich(
                db, include_early_career_researchers=True, include_roles=[ROLE_1]
            )
            assert {p[PERSON_ID] for p in person_list} == {PERSON_ID_1, PERSON_ID_2}


def _enrich_early_career_researchers(db, get_request_handler, max_workers=1):
    person_list = get_persons_to_enrich(
        db, include_early_career_researchers=True, include_roles=[]
    )
    enrich_and_update_person_list(
        db, person_list, get_request_handler, max_workers=max_workers
    )


class TestEnrichAndUpdatePersonList:
    def test_should_not_fail_if_database_is_empty(self):
        with populated_in_memory_database(EMPTY_DATASET) as db:
            _enrich_early_career_researchers(db, MapRequestHandler({}))

    def test_should_import_one_by_orcid(self):
        response_by_url_map = {
            get_crossref_works_by_orcid_url(ORCID_1): get_crossref_response([{
                'DOI': DOI_1,
                'author': [{
                    'ORCID': ORCID_1
                }]
            }])
        }
        dataset = {
            'person': [ECR_1],
            'person_membership': [ORCID_MEMBERSHIP_1]
        }
        with populated_in_memory_database(dataset) as db:
            _enrich_early_career_researchers(db, MapRequestHandler(response_by_url_map))

            manuscript_df = db.manuscript.read_frame().reset_index()
            LOGGER.debug('manuscript_df:\n%s', manuscript_df)
            assert set(manuscript_df[DOI]) == {DOI_1}

            manuscript_version_df = db.manuscript_version.read_frame().reset_index()
            LOGGER.debug('manuscript_version_df:\n%s', manuscript_version_df)
            assert set(manuscript_version_df['is_published']) == {True}

    def test_should_import_one_by_full_name(self):
        full_name = ' '.join([FIRST_NAME_1, LAST_NAME_1])
        response_by_url_map = {
            get_crossref_works_by_full_name_url(full_name): get_crossref_response([{
                'DOI': DOI_1,
                'author': [{
                    'given': FIRST_NAME_1,
                    'family': LAST_NAME_1
                }]
            }])
        }
        # not adding ORCID membership, this will trigger search by name instead
        dataset = {
            'person': [ECR_1]
        }
        with populated_in_memory_database(dataset) as db:
            _enrich_early_career_researchers(db, MapRequestHandler(response_by_url_map))

            manuscript_df = db.manuscript.read_frame().reset_index()
            LOGGER.debug('manuscript_df:\n%s', manuscript_df)
            assert set(manuscript_df[DOI]) == {DOI_1}

            manuscript_version_df = db.manuscript_version.read_frame().reset_index()
            LOGGER.debug('manuscript_version_df:\n%s', manuscript_version_df)
            assert set(manuscript_version_df['is_published']) == {True}

    def test_should_import_one_if_existing_doi_is_different(self):
        response_by_url_map = {
            get_crossref_works_by_orcid_url(ORCID_1): get_crossref_response([{
                'DOI': DOI_2,
                'author': [{
                    'ORCID': ORCID_1
                }]
            }])
        }
        dataset = {
            'manuscript': [{
                MANUSCRIPT_ID: MANUSCRIPT_ID_1,
                DOI: DOI_1
            }],
            'person': [ECR_1],
            'person_membership': [ORCID_MEMBERSHIP_1]
        }
        with populated_in_memory_database(dataset) as db:
            _enrich_early_career_researchers(db, MapRequestHandler(response_by_url_map))

            df = db.manuscript.read_frame().reset_index()
            LOGGER.debug('df:\n%s', df)
            assert set(df[DOI]) == {DOI_1, DOI_2}

    def test_should_not_import_one_if_doi_already_exists(self):
        response_by_url_map = {
            get_crossref_works_by_orcid_url(ORCID_1): get_crossref_response([{
                'DOI': DOI_1,
                'author': [{
                    'ORCID': ORCID_1
                }]
            }])
        }
        dataset = {
            'manuscript': [{
                MANUSCRIPT_ID: MANUSCRIPT_ID_1,
                DOI: DOI_1
            }],
            'person': [ECR_1],
            'person_membership': [ORCID_MEMBERSHIP_1]
        }
        with populated_in_memory_database(dataset) as db:
            _enrich_early_career_researchers(db, MapRequestHandler(response_by_url_map))

            df = db.manuscript.read_frame().reset_index()
            LOGGER.debug('df:\n%s', df)
            assert list(df[DOI]) == [DOI_1]

    def test_should_not_import_one_if_doi_already_exists_with_different_case(self):
        doi_1_original = 'Doi 1'
        doi_1_new = 'doi 1'
        response_by_url_map = {
            get_crossref_works_by_orcid_url(ORCID_1): get_crossref_response([{
                'DOI': doi_1_new,
                'author': [{
                    'ORCID': ORCID_1
                }]
            }])
        }
        dataset = {
            'manuscript': [{
                MANUSCRIPT_ID: MANUSCRIPT_ID_1,
                DOI: doi_1_original
            }],
            'person': [ECR_1],
            'person_membership': [ORCID_MEMBERSHIP_1]
        }
        with populated_in_memory_database(dataset) as db:
            _enrich_early_career_researchers(db, MapRequestHandler(response_by_url_map))

            df = db.manuscript.read_frame().reset_index()
            LOGGER.debug('df:\n%s', df)
            assert list(df[DOI]) == [doi_1_original]


class TestParseIntList:
    def test_should_return_default_value_for_none(self):
        assert parse_int_list(None, [1, 2, 3]) == [1, 2, 3]

    def test_should_return_default_value_for_empty_string(self):
        assert parse_int_list('', [1, 2, 3]) == [1, 2, 3]

    def test_should_parse_multiple_values(self):
        assert parse_int_list('100, 200, 300', [1, 2, 3]) == [100, 200, 300]


class TestDecorateGetRequestHandler:
    @pytest.fixture(autouse=True)
    def create_str_cache_mock(self):
        with patch.object(enrich_data_module, 'create_str_cache') as create_str_cache_mock:
            yield create_str_cache_mock

    def test_should_call_through_with_decorators(self, mock_f):
        app_config = ConfigParser()
        decorated_get_request_handler = decorate_get_request_handler(
            mock_f, app_config, cache_dir=None
        )
        assert decorated_get_request_handler(URL_1) == mock_f.return_value
        assert decorate_get_request_handler != mock_f  # pylint: disable=comparison-with-callable

    def test_should_pass_expire_after_secs_to_cache(self, create_str_cache_mock, mock_f):
        cache_dir = '.cache/dir'
        decorate_get_request_handler(mock_f, dict_to_config(
            {}), cache_dir=cache_dir, expire_after_secs=123)
        create_str_cache_mock.assert_called_with(
            ANY,
            cache_dir=cache_dir,
            suffix='.json',
            expire_after_secs=123
        )


class TestMain:
    @pytest.fixture(name='get_app_config_mock', autouse=True)
    def _get_app_config(self):
        with patch.object(enrich_data_module, 'get_app_config') as get_app_config_mock:
            get_app_config_mock.return_value = dict_to_config({})
            yield get_app_config_mock

    @pytest.fixture(name='decorate_get_request_handler_mock', autouse=True)
    def _decorate_get_request_handler(self):
        with patch.object(enrich_data_module, 'decorate_get_request_handler') \
                as decorate_get_request_handler_mock:

            yield decorate_get_request_handler_mock

    @pytest.fixture(name='connect_managed_configured_database_mock', autouse=True)
    def _connect_managed_configured_database(self):
        with patch.object(enrich_data_module, 'connect_managed_configured_database') \
                as connect_managed_configured_database_mock:

            yield connect_managed_configured_database_mock

    @pytest.fixture(name='get_persons_to_enrich_mock', autouse=True)
    def _get_persons_to_enrich(self):
        with patch.object(enrich_data_module, 'get_persons_to_enrich') \
                as get_persons_to_enrich_mock:

            yield get_persons_to_enrich_mock

    @pytest.fixture(name='enrich_and_update_person_list_mock', autouse=True)
    def _enrich_and_update_person_list(self):
        with patch.object(enrich_data_module, 'enrich_and_update_person_list') \
                as enrich_and_update_person_list_mock:

            yield enrich_and_update_person_list_mock

    def test_should_parse_expire_after_secs_and_pass_to_decorate_get_request_handler(
            self, get_app_config_mock, decorate_get_request_handler_mock):

        get_app_config_mock.return_value = dict_to_config({
            'crossref': {
                'expire_after_secs': '123'
            }
        })

        main()
        decorate_get_request_handler_mock.assert_called_with(
            ANY,
            ANY,
            cache_dir=ANY,
            expire_after_secs=123
        )

    def test_should_parse_false_early_career_researcher_and_pass_to_get_persons_to_enrich(
            self, get_app_config_mock, get_persons_to_enrich_mock):

        get_app_config_mock.return_value = dict_to_config({
            'enrich-data': {
                'include_early_career_researcher': 'false'
            }
        })

        main()
        get_persons_to_enrich_mock.assert_called_with(
            ANY,
            include_early_career_researchers=False,
            include_roles=ANY
        )

    def test_should_parse_true_early_career_researcher_and_pass_to_get_persons_to_enrich(
            self, get_app_config_mock, get_persons_to_enrich_mock):

        get_app_config_mock.return_value = dict_to_config({
            'enrich-data': {
                'include_early_career_researcher': 'true'
            }
        })

        main()
        get_persons_to_enrich_mock.assert_called_with(
            ANY,
            include_early_career_researchers=True,
            include_roles=ANY
        )

    def test_should_parse_roles_and_pass_to_get_persons_to_enrich(
            self, get_app_config_mock, get_persons_to_enrich_mock):

        get_app_config_mock.return_value = dict_to_config({
            'enrich-data': {
                'include_roles': '%s, %s' % (ROLE_1, ROLE_2)
            }
        })

        main()
        get_persons_to_enrich_mock.assert_called_with(
            ANY,
            include_early_career_researchers=ANY,
            include_roles=[ROLE_1, ROLE_2]
        )

    def test_should_pass_correct_parameters_to_enrich_and_update_person_list(
            self,
            connect_managed_configured_database_mock,
            get_persons_to_enrich_mock,
            enrich_and_update_person_list_mock,
            decorate_get_request_handler_mock):

        main()
        enrich_and_update_person_list_mock.assert_called_with(
            connect_managed_configured_database_mock.return_value.__enter__.return_value,
            get_persons_to_enrich_mock.return_value,
            get_request_handler=decorate_get_request_handler_mock.return_value,
            max_workers=DEFAULT_MAX_WORKERS
        )
