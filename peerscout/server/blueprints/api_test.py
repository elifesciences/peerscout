from __future__ import absolute_import

from configparser import ConfigParser
import logging
import json
from contextlib import contextmanager
from unittest.mock import patch
from urllib.parse import urlencode

import pytest

from flask import Flask
from flask.testing import FlaskClient

from ...utils.config import dict_to_config
from ..config.search_config import SEARCH_SECTION_PREFIX

from ...shared.database import populated_in_memory_database

from . import api as api_module
from .api import create_api_blueprint

LOGGER = logging.getLogger(__name__)

VALUE_1 = 'value1'
VALUE_2 = 'value2'
VALUE_3 = 'value3'

MANUSCRIPT_NO_1 = '12345'
MANUSCRIPT_NO_2 = '22222'
LIMIT_1 = 123

SEARCH_TYPE_1 = 'search_type1'
SEARCH_TYPE_2 = 'search_type2'

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

@pytest.mark.slow
class TestApiBlueprint:
  class TestKeywords:
    def test_should_return_keywords(self):
      config = ConfigParser()
      with patch.object(api_module, 'RecommendReviewers') as RecommendReviewers_mock:
        with _api_test_client(config, {}) as test_client:
          RecommendReviewers_mock.return_value.get_all_keywords.return_value = [VALUE_1, VALUE_2]
          response = test_client.get('/keywords')
          assert _get_ok_json(response) == [VALUE_1, VALUE_2]

  class TestSubjectAreas:
    def test_should_return_subject_areas(self):
      config = ConfigParser()
      with patch.object(api_module, 'RecommendReviewers') as RecommendReviewers_mock:
        with _api_test_client(config, {}) as test_client:
          RecommendReviewers_mock.return_value.get_all_subject_areas.return_value = [VALUE_1, VALUE_2]
          response = test_client.get('/subject-areas')
          assert _get_ok_json(response) == [VALUE_1, VALUE_2]

  class TestConfig:
    def test_should_return_client_config(self):
      client_config = {
        'some key': VALUE_1
      }
      config = dict_to_config({
        'client': client_config
      })
      with patch.object(api_module, 'RecommendReviewers') as RecommendReviewers_mock:
        with _api_test_client(config, {}) as test_client:
          RecommendReviewers_mock.return_value.get_all_subject_areas.return_value = [VALUE_1, VALUE_2]
          response = test_client.get('/config')
          assert _get_ok_json(response) == client_config

  class TestRecommendWithoutAuth:
    def test_should_return_400_without_args(self):
      config = ConfigParser()
      with _api_test_client(config, {}) as test_client:
        response = test_client.get('/recommend-reviewers')
        assert response.status_code == 400

    def test_should_return_results_by_manuscript_no(self):
      config = ConfigParser()
      with patch.object(api_module, 'RecommendReviewers') as RecommendReviewers_mock:
        with _api_test_client(config, {}) as test_client:
          RecommendReviewers_mock.return_value.recommend.return_value = SOME_RESPONSE
          response = test_client.get('/recommend-reviewers?' + urlencode({
            'manuscript_no': MANUSCRIPT_NO_1
          }))
          assert _get_ok_json(response) == SOME_RESPONSE
          _assert_partial_called_with(
            RecommendReviewers_mock.return_value.recommend,
            manuscript_no=MANUSCRIPT_NO_1
          )

    def test_should_return_results_by_keywords(self):
      config = ConfigParser()
      with patch.object(api_module, 'RecommendReviewers') as RecommendReviewers_mock:
        with _api_test_client(config, {}) as test_client:
          RecommendReviewers_mock.return_value.recommend.return_value = SOME_RESPONSE
          response = test_client.get('/recommend-reviewers?' + urlencode({
            'keywords': VALUE_1,
            'subject_area': VALUE_2,
            'abstract': VALUE_3
          }))
          assert _get_ok_json(response) == SOME_RESPONSE
          _assert_partial_called_with(
            RecommendReviewers_mock.return_value.recommend,
            keywords=VALUE_1,
            subject_area=VALUE_2,
            abstract=VALUE_3
          )

    def test_should_pass_limit_to_recommend_method(self):
      config = ConfigParser()
      with patch.object(api_module, 'RecommendReviewers') as RecommendReviewers_mock:
        with _api_test_client(config, {}) as test_client:
          RecommendReviewers_mock.return_value.recommend.return_value = SOME_RESPONSE
          test_client.get('/recommend-reviewers?' + urlencode({
            'limit': LIMIT_1,
            'manuscript_no': MANUSCRIPT_NO_1
          }))
          _assert_partial_called_with(
            RecommendReviewers_mock.return_value.recommend,
            limit=LIMIT_1
          )

    def test_should_default_to_none_role(self):
      config = dict_to_config({})
      with patch.object(api_module, 'RecommendReviewers') as RecommendReviewers_mock:
        with _api_test_client(config, {}) as test_client:
          RecommendReviewers_mock.return_value.recommend.return_value = SOME_RESPONSE
          test_client.get('/recommend-reviewers?' + urlencode({
            'manuscript_no': MANUSCRIPT_NO_1
          }))
          _assert_partial_called_with(
            RecommendReviewers_mock.return_value.recommend,
            role=None
          )

    def test_should_pass_role_from_search_config_to_recommend_method(self):
      config = dict_to_config({
        SEARCH_SECTION_PREFIX + SEARCH_TYPE_1: {
          'filter_by_role': VALUE_1
        }
      })
      with patch.object(api_module, 'RecommendReviewers') as RecommendReviewers_mock:
        with _api_test_client(config, {}) as test_client:
          RecommendReviewers_mock.return_value.recommend.return_value = SOME_RESPONSE
          test_client.get('/recommend-reviewers?' + urlencode({
            'manuscript_no': MANUSCRIPT_NO_1,
            'search_type': SEARCH_TYPE_1
          }))
          _assert_partial_called_with(
            RecommendReviewers_mock.return_value.recommend,
            role=VALUE_1
          )

    def test_should_reject_unknown_search_type(self):
      config = dict_to_config({
        SEARCH_SECTION_PREFIX + SEARCH_TYPE_1: {
          'filter_by_role': VALUE_1
        }
      })
      with patch.object(api_module, 'RecommendReviewers') as RecommendReviewers_mock:
        with _api_test_client(config, {}) as test_client:
          RecommendReviewers_mock.return_value.recommend.return_value = SOME_RESPONSE
          response = test_client.get('/recommend-reviewers?' + urlencode({
            'manuscript_no': MANUSCRIPT_NO_1,
            'search_type': SEARCH_TYPE_2
          }))
          assert response.status_code == 400

    def test_should_cache_with_same_parameters(self):
      config = ConfigParser()
      with patch.object(api_module, 'RecommendReviewers') as RecommendReviewers_mock:
        with _api_test_client(config, {}) as test_client:
          RecommendReviewers_mock.return_value.recommend.return_value = SOME_RESPONSE
          test_client.get('/recommend-reviewers?' + urlencode({
            'manuscript_no': MANUSCRIPT_NO_1
          }))
          test_client.get('/recommend-reviewers?' + urlencode({
            'manuscript_no': MANUSCRIPT_NO_1
          }))
          RecommendReviewers_mock.return_value.recommend.assert_called_once()

    def test_should_not_cache_with_different_parameters(self):
      config = ConfigParser()
      with patch.object(api_module, 'RecommendReviewers') as RecommendReviewers_mock:
        with _api_test_client(config, {}) as test_client:
          RecommendReviewers_mock.return_value.recommend.return_value = SOME_RESPONSE
          test_client.get('/recommend-reviewers?' + urlencode({
            'manuscript_no': MANUSCRIPT_NO_1
          }))
          test_client.get('/recommend-reviewers?' + urlencode({
            'manuscript_no': MANUSCRIPT_NO_2
          }))
          assert RecommendReviewers_mock.return_value.recommend.call_count == 2
