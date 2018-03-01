from __future__ import absolute_import

from configparser import ConfigParser
import logging
import json
from contextlib import contextmanager
from unittest.mock import patch, Mock, MagicMock
from urllib.parse import urlencode

import pytest

from flask import Flask
from flask.testing import FlaskClient
from werkzeug.exceptions import Forbidden

from ...utils.config import dict_to_config
from ..config.search_config import SEARCH_SECTION_PREFIX

from ...shared.database import populated_in_memory_database

from peerscout.server.services.test_data import (
  PERSON1,
  PERSON_ID1
)

from . import api as api_module
from .api import create_api_blueprint, ApiAuth

LOGGER = logging.getLogger(__name__)

VALUE_1 = 'value1'
VALUE_2 = 'value2'
VALUE_3 = 'value3'

DOMAIN_1 = 'domain1'
ROLE_1 = 'role1'
ROLE_2 = 'role2'
EMAIL_1 = 'email1'

MANUSCRIPT_NO_1 = '12345'
MANUSCRIPT_NO_2 = '22222'
LIMIT_1 = 123

SEARCH_TYPE_1 = 'search_type1'
SEARCH_TYPE_2 = 'search_type2'
SEARCH_TYPE_3 = 'search_type3'
SEARCH_TYPE_TITLE_1 = 'Search Type 1'
SEARCH_TYPE_TITLE_2 = 'Search Type 2'
SEARCH_TYPE_TITLE_3 = 'Search Type 3'

SOME_RESPONSE = {
  'some-response': VALUE_1
}

def setup_module():
  logging.root.handlers = []
  logging.basicConfig(level='DEBUG')

@contextmanager
def _api_test_client(config, dataset):
  m = api_module
  with populated_in_memory_database(dataset, autocommit=True) as db:
    with patch.object(m, 'connect_configured_database') as connect_configured_database_mock:
      connect_configured_database_mock.return_value = db
      blueprint, reload_api = create_api_blueprint(config)
      app = Flask(__name__)
      app.register_blueprint(blueprint)
      assert reload_api
      yield app.test_client()

def _get_json(response):
  return json.loads(response.data.decode('utf-8'))

def _get_ok_json(response):
  assert response.status_code == 200
  return _get_json(response)

def _assert_partial_called_with(mock, **kwargs):
  mock.assert_called()
  assert {k: v for k, v in mock.call_args[1].items() if k in kwargs} == kwargs

def _named_mock(name, **kwargs):
  mock = Mock(name=name, **kwargs)
  mock.__name__ = name
  return mock

def _setup_flask_auth0_mock_email(MockFlaskAuth0, **kwargs):
  def wrapper(f):
    result = lambda: f(**kwargs)
    result.__name__ = f.__name__
    return result

  _wrap_request_handler = MockFlaskAuth0.return_value.wrap_request_handler
  _wrap_request_handler.side_effect = wrapper
  return MockFlaskAuth0

@pytest.fixture(name='MockRecommendReviewers')
def _mock_recommend_reviewers():
  with patch.object(api_module, 'RecommendReviewers') as MockRecommendReviewers:
    MockRecommendReviewers.return_value.recommend.return_value = SOME_RESPONSE
    yield MockRecommendReviewers

@pytest.fixture(name='MockFlaskAuth0')
def _mock_flask_auth_0():
  with patch.object(api_module, 'FlaskAuth0') as MockFlaskAuth0:
    yield MockFlaskAuth0

@pytest.mark.slow
class TestApiBlueprint:
  class TestKeywords:
    def test_should_return_keywords(self, MockRecommendReviewers):
      config = ConfigParser()
      with _api_test_client(config, {}) as test_client:
        MockRecommendReviewers.return_value.get_all_keywords.return_value = [VALUE_1, VALUE_2]
        response = test_client.get('/keywords')
        assert _get_ok_json(response) == [VALUE_1, VALUE_2]

  class TestSubjectAreas:
    def test_should_return_subject_areas(self, MockRecommendReviewers):
      config = ConfigParser()
      with _api_test_client(config, {}) as test_client:
        MockRecommendReviewers.return_value.get_all_subject_areas.return_value = [VALUE_1, VALUE_2]
        response = test_client.get('/subject-areas')
        assert _get_ok_json(response) == [VALUE_1, VALUE_2]

  class TestConfig:
    def test_should_return_client_config(self, MockRecommendReviewers):
      client_config = {
        'some key': VALUE_1
      }
      config = dict_to_config({
        'client': client_config
      })
      with _api_test_client(config, {}) as test_client:
        MockRecommendReviewers.return_value.get_all_subject_areas.return_value = [VALUE_1, VALUE_2]
        response = test_client.get('/config')
        assert _get_ok_json(response) == client_config

  class TestSearchTypes:
    @pytest.mark.parametrize('email, required_role, auth0_domain', [
      (None, None, None),
      (None, None, DOMAIN_1),
      ('data@science.org', ROLE_1, DOMAIN_1)
    ])
    def test_should_return_all_search_types_if_authorisation_is_not_required(
      self, MockRecommendReviewers, MockFlaskAuth0, email, required_role, auth0_domain):

      _setup_flask_auth0_mock_email(MockFlaskAuth0, email=email)

      config = dict_to_config({
        'auth': {'allowed_ips': '', 'valid_email_domains': 'science.org'},
        'client': {'auth0_domain': DOMAIN_1},
        SEARCH_SECTION_PREFIX + SEARCH_TYPE_1: {
          'required_role': required_role or '',
          'title': SEARCH_TYPE_TITLE_1
        },
        SEARCH_SECTION_PREFIX + SEARCH_TYPE_2: {
          'required_role': required_role or '',
          'title': SEARCH_TYPE_TITLE_2
        }
      })

      with _api_test_client(config, {}) as test_client:
        response = test_client.get('/search-types')
        assert _get_ok_json(response) == [{
          'search_type': SEARCH_TYPE_1,
          'title': SEARCH_TYPE_TITLE_1
        }, {
          'search_type': SEARCH_TYPE_2,
          'title': SEARCH_TYPE_TITLE_2
        }]

    def test_should_filter_search_types_by_required_role(
      self, MockRecommendReviewers, MockFlaskAuth0):

      _setup_flask_auth0_mock_email(MockFlaskAuth0, email=EMAIL_1)

      config = dict_to_config({
        'auth': {'allowed_ips': ''},
        'client': {'auth0_domain': DOMAIN_1},
        SEARCH_SECTION_PREFIX + SEARCH_TYPE_1: {
          'required_role': ROLE_1,
          'title': SEARCH_TYPE_TITLE_1
        },
        SEARCH_SECTION_PREFIX + SEARCH_TYPE_2: {
          'required_role': ROLE_2,
          'title': SEARCH_TYPE_TITLE_2
        },
        SEARCH_SECTION_PREFIX + SEARCH_TYPE_3: {
          'required_role': '',
          'title': SEARCH_TYPE_TITLE_3
        }
      })

      with _api_test_client(config, {}) as test_client:
        get_user_roles_by_email = MockRecommendReviewers.return_value.get_user_roles_by_email
        get_user_roles_by_email.return_value = {ROLE_1}
        response = test_client.get('/search-types')
        assert _get_ok_json(response) == [{
          'search_type': SEARCH_TYPE_1,
          'title': SEARCH_TYPE_TITLE_1
        }, {
          'search_type': SEARCH_TYPE_3,
          'title': SEARCH_TYPE_TITLE_3
        }]

  class TestRecommendWithoutAuth:
    def test_should_return_400_without_args(self, MockRecommendReviewers):
      config = ConfigParser()
      with _api_test_client(config, {}) as test_client:
        response = test_client.get('/recommend-reviewers')
        assert response.status_code == 400

    def test_should_return_results_by_manuscript_no(self, MockRecommendReviewers):
      config = ConfigParser()
      with _api_test_client(config, {}) as test_client:
        MockRecommendReviewers.return_value.recommend.return_value = SOME_RESPONSE
        response = test_client.get('/recommend-reviewers?' + urlencode({
          'manuscript_no': MANUSCRIPT_NO_1
        }))
        assert _get_ok_json(response) == SOME_RESPONSE
        _assert_partial_called_with(
          MockRecommendReviewers.return_value.recommend,
          manuscript_no=MANUSCRIPT_NO_1
        )

    def test_should_return_results_by_keywords(self, MockRecommendReviewers):
      config = ConfigParser()
      with _api_test_client(config, {}) as test_client:
        MockRecommendReviewers.return_value.recommend.return_value = SOME_RESPONSE
        response = test_client.get('/recommend-reviewers?' + urlencode({
          'keywords': VALUE_1,
          'subject_area': VALUE_2,
          'abstract': VALUE_3
        }))
        assert _get_ok_json(response) == SOME_RESPONSE
        _assert_partial_called_with(
          MockRecommendReviewers.return_value.recommend,
          keywords=VALUE_1,
          subject_area=VALUE_2,
          abstract=VALUE_3
        )

    def test_should_pass_limit_to_recommend_method(self, MockRecommendReviewers):
      config = ConfigParser()
      with _api_test_client(config, {}) as test_client:
        test_client.get('/recommend-reviewers?' + urlencode({
          'limit': LIMIT_1,
          'manuscript_no': MANUSCRIPT_NO_1
        }))
        _assert_partial_called_with(
          MockRecommendReviewers.return_value.recommend,
          limit=LIMIT_1
        )

    def test_should_default_to_none_role(self, MockRecommendReviewers):
      config = dict_to_config({})
      with _api_test_client(config, {}) as test_client:
        test_client.get('/recommend-reviewers?' + urlencode({
          'manuscript_no': MANUSCRIPT_NO_1
        }))
        _assert_partial_called_with(
          MockRecommendReviewers.return_value.recommend,
          role=None
        )

    def test_should_pass_search_params_from_search_config_to_recommend_method(self, MockRecommendReviewers):
      config = dict_to_config({
        SEARCH_SECTION_PREFIX + SEARCH_TYPE_1: {
          'filter_by_role': VALUE_1,
          'recommend_relationship_types': VALUE_2,
          'recommend_stage_names': VALUE_3
        }
      })
      with _api_test_client(config, {}) as test_client:
        MockRecommendReviewers.return_value.recommend.return_value = SOME_RESPONSE
        test_client.get('/recommend-reviewers?' + urlencode({
          'manuscript_no': MANUSCRIPT_NO_1,
          'search_type': SEARCH_TYPE_1
        }))
        _assert_partial_called_with(
          MockRecommendReviewers.return_value.recommend,
          role=VALUE_1,
          recommend_relationship_types=[VALUE_2],
          recommend_stage_names=[VALUE_3]
        )

    def test_should_reject_unknown_search_type(self, MockRecommendReviewers):
      config = dict_to_config({
        SEARCH_SECTION_PREFIX + SEARCH_TYPE_1: {
          'filter_by_role': VALUE_1
        }
      })
      with _api_test_client(config, {}) as test_client:
        response = test_client.get('/recommend-reviewers?' + urlencode({
          'manuscript_no': MANUSCRIPT_NO_1,
          'search_type': SEARCH_TYPE_2
        }))
        assert response.status_code == 400

    def test_should_cache_with_same_parameters(self, MockRecommendReviewers):
      config = ConfigParser()
      with _api_test_client(config, {}) as test_client:
        test_client.get('/recommend-reviewers?' + urlencode({
          'manuscript_no': MANUSCRIPT_NO_1
        }))
        test_client.get('/recommend-reviewers?' + urlencode({
          'manuscript_no': MANUSCRIPT_NO_1
        }))
        MockRecommendReviewers.return_value.recommend.assert_called_once()

    def test_should_not_cache_with_different_parameters(self, MockRecommendReviewers):
      config = ConfigParser()
      with _api_test_client(config, {}) as test_client:
        test_client.get('/recommend-reviewers?' + urlencode({
          'manuscript_no': MANUSCRIPT_NO_1
        }))
        test_client.get('/recommend-reviewers?' + urlencode({
          'manuscript_no': MANUSCRIPT_NO_2
        }))
        assert MockRecommendReviewers.return_value.recommend.call_count == 2

  class TestRecommendWithAuth:
    def test_should_allow_search_type_for_person_with_matching_role(
      self, MockRecommendReviewers, MockFlaskAuth0):

      _setup_flask_auth0_mock_email(MockFlaskAuth0, email=EMAIL_1)

      config = dict_to_config({
        'auth': {'allowed_ips': ''},
        'client': {'auth0_domain': DOMAIN_1},
        SEARCH_SECTION_PREFIX + SEARCH_TYPE_1: {
          'required_role': ROLE_1
        }
      })
      with _api_test_client(config, {}) as test_client:
        user_has_role_by_email = MockRecommendReviewers.return_value.user_has_role_by_email
        user_has_role_by_email.return_value = True
        response = test_client.get('/recommend-reviewers?' + urlencode({
          'manuscript_no': MANUSCRIPT_NO_1,
          'search_type': SEARCH_TYPE_1
        }))
        user_has_role_by_email.assert_called_with(
          email=EMAIL_1, role=ROLE_1
        )
        assert response.status_code == 200

    def test_should_not_allow_search_type_for_person_without_matching_role(
      self, MockRecommendReviewers, MockFlaskAuth0):

      _setup_flask_auth0_mock_email(MockFlaskAuth0, email=EMAIL_1)

      config = dict_to_config({
        'auth': {'allowed_ips': ''},
        'client': {'auth0_domain': DOMAIN_1},
        SEARCH_SECTION_PREFIX + SEARCH_TYPE_1: {
          'required_role': ROLE_1
        }
      })
      with _api_test_client(config, {}) as test_client:
        user_has_role_by_email = MockRecommendReviewers.return_value.user_has_role_by_email
        user_has_role_by_email.return_value = False
        response = test_client.get('/recommend-reviewers?' + urlencode({
          'manuscript_no': MANUSCRIPT_NO_1,
          'search_type': SEARCH_TYPE_1
        }))
        user_has_role_by_email.assert_called_with(
          email=EMAIL_1, role=ROLE_1
        )
        assert response.status_code == 403

    def test_should_allow_search_type_and_not_check_person_role_if_no_role_is_required(
      self, MockRecommendReviewers, MockFlaskAuth0):

      _setup_flask_auth0_mock_email(MockFlaskAuth0, email=EMAIL_1)

      config = dict_to_config({
        'auth': {'allowed_ips': ''},
        'client': {'auth0_domain': DOMAIN_1},
        SEARCH_SECTION_PREFIX + SEARCH_TYPE_1: {
          'required_role': ''
        }
      })
      with _api_test_client(config, {}) as test_client:
        user_has_role_by_email = MockRecommendReviewers.return_value.user_has_role_by_email
        response = test_client.get('/recommend-reviewers?' + urlencode({
          'manuscript_no': MANUSCRIPT_NO_1,
          'search_type': SEARCH_TYPE_1
        }))
        user_has_role_by_email.assert_not_called()
        assert response.status_code == 200

class TestApiAuth:
  @pytest.fixture(name='DummyAppContext', autouse=True)
  def _dummy_app_context(self):
    app = Flask(__name__)
    with app.app_context() as app_context:
      yield app_context

  def test_should_allow_local_ips_by_default(self, MockFlaskAuth0):
    ApiAuth(dict_to_config({}), {'auth0_domain': VALUE_1})
    _assert_partial_called_with(MockFlaskAuth0, allowed_ips={'127.0.0.1'})

  class TestWrapSearch:
    def test_should_not_wrap_with_auth_if_no_auth0_domain_is_present(self):
      config = dict_to_config({})
      client_config = {}
      api_auth = ApiAuth(config, client_config)
      f = Mock()
      assert api_auth.wrap_search(f) == f

    def test_should_wrap_with_auth_if_auth0_domain_is_present(self, MockFlaskAuth0):
      _setup_flask_auth0_mock_email(MockFlaskAuth0, email=None)

      api_auth = ApiAuth(dict_to_config({}), {'auth0_domain': VALUE_1})
      _assert_partial_called_with(MockFlaskAuth0, domain=VALUE_1)

      f = _named_mock(name='f')
      wrapped_f = api_auth.wrap_search(f)
      assert wrapped_f != f
      assert wrapped_f() == f.return_value

    def test_should_reject_search_types_for_emails_not_associated_with_required_role(self, MockFlaskAuth0):
      _setup_flask_auth0_mock_email(MockFlaskAuth0, email=EMAIL_1)

      user_has_role_by_email = Mock(name='user_has_role_by_email')
      user_has_role_by_email.return_value = False
      api_auth = ApiAuth(
        dict_to_config({'auth': {
          'valid_email_domains': 'other.org'
        }}),
        {'auth0_domain': DOMAIN_1},
        search_config={SEARCH_TYPE_1: {'required_role': ROLE_1}},
        user_has_role_by_email=user_has_role_by_email,
        get_search_type=lambda: SEARCH_TYPE_1
      )

      f = _named_mock(name='f')
      wrapped_f = api_auth.wrap_search(f)
      assert wrapped_f != f
      with pytest.raises(Forbidden):
        wrapped_f()
      user_has_role_by_email.assert_called_with(email=EMAIL_1, role=ROLE_1)

    def test_should_allow_search_types_for_emails_part_of_configured_domain(self, MockFlaskAuth0):
      _setup_flask_auth0_mock_email(MockFlaskAuth0, email='data@science.org')

      user_has_role_by_email = Mock(name='user_has_role_by_email')
      user_has_role_by_email.return_value = False
      api_auth = ApiAuth(
        dict_to_config({'auth': {
          'valid_email_domains': 'science.org'
        }}),
        {'auth0_domain': DOMAIN_1},
        search_config={SEARCH_TYPE_1: {'required_role': ROLE_1}},
        user_has_role_by_email=user_has_role_by_email,
        get_search_type=lambda: SEARCH_TYPE_1
      )

      f = _named_mock(name='f')
      wrapped_f = api_auth.wrap_search(f)
      assert wrapped_f != f
      assert wrapped_f() == f.return_value
