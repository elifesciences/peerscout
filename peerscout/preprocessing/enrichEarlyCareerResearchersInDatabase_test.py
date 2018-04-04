import logging
import json
from typing import Dict
from unittest.mock import Mock
from configparser import ConfigParser

from ..shared.database import populated_in_memory_database

from .enrichEarlyCareerResearchersInDatabase import (
  extract_manuscript,
  enrich_early_career_researchers,
  get_crossref_works_by_orcid_url,
  get_crossref_works_by_full_name_url,
  parse_int_list,
  decorate_get_request_handler
)

URL_1 = 'test://dummy.url'

TITLE1 = 'Title 1'
ABSTRACT1 = 'Abstract 1'
MANUSCRIPT_TYPE1 = 'Manuscript Type 1'

def setup_module():
  logging.basicConfig(level=logging.DEBUG)

def get_logger():
  return logging.getLogger(__name__)

class TestExtractManuscript(object):
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

# Schema field names
PERSON_ID = 'person_id'
MANUSCRIPT_ID = 'manuscript_id'
DOI = 'doi'

PERSON_ID_1 = 'person1'

FIRST_NAME_1 = 'Jon'
LAST_NAME_1 = 'Smith'

ECR_1 = {
  PERSON_ID: PERSON_ID_1,
  'first_name': FIRST_NAME_1,
  'last_name': LAST_NAME_1,
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

def get_crossref_response(items):
  return json.dumps({
    'message': {
      'items': items
    }
  })

EMPTY_DATASET = {}

class TestEnrichEarlyCareerResearchers(object):
  def test_should_not_fail_if_database_is_empty(self):
    with populated_in_memory_database(EMPTY_DATASET) as db:
      enrich_early_career_researchers(db, MapRequestHandler({}))

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
      enrich_early_career_researchers(db, MapRequestHandler(response_by_url_map))

      manuscript_df = db.manuscript.read_frame().reset_index()
      get_logger().debug('manuscript_df:\n%s', manuscript_df)
      assert set(manuscript_df[DOI]) == {DOI_1}

      manuscript_version_df = db.manuscript_version.read_frame().reset_index()
      get_logger().debug('manuscript_version_df:\n%s', manuscript_version_df)
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
    dataset = {
      'person': [ECR_1]
      # not adding ORCID membership, this will trigger search by name instead
    }
    with populated_in_memory_database(dataset) as db:
      enrich_early_career_researchers(db, MapRequestHandler(response_by_url_map))

      manuscript_df = db.manuscript.read_frame().reset_index()
      get_logger().debug('manuscript_df:\n%s', manuscript_df)
      assert set(manuscript_df[DOI]) == {DOI_1}

      manuscript_version_df = db.manuscript_version.read_frame().reset_index()
      get_logger().debug('manuscript_version_df:\n%s', manuscript_version_df)
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
      enrich_early_career_researchers(db, MapRequestHandler(response_by_url_map))

      df = db.manuscript.read_frame().reset_index()
      get_logger().debug('df:\n%s', df)
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
      enrich_early_career_researchers(db, MapRequestHandler(response_by_url_map))

      df = db.manuscript.read_frame().reset_index()
      get_logger().debug('df:\n%s', df)
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
      enrich_early_career_researchers(db, MapRequestHandler(response_by_url_map))

      df = db.manuscript.read_frame().reset_index()
      get_logger().debug('df:\n%s', df)
      assert list(df[DOI]) == [doi_1_original]

class TestParseIntList(object):
  def test_should_return_default_value_for_none(self):
    assert parse_int_list(None, [1, 2, 3]) == [1, 2, 3]

  def test_should_return_default_value_for_empty_string(self):
    assert parse_int_list('', [1, 2, 3]) == [1, 2, 3]

  def test_should_parse_multiple_values(self):
    assert parse_int_list('100, 200, 300', [1, 2, 3]) == [100, 200, 300]

class TestDecorateGetRequestHandler(object):
  def test_should_call_through_with_decorators(self):
    app_config = ConfigParser()
    get_request_handler = Mock()
    decorated_get_request_handler = decorate_get_request_handler(
      get_request_handler, app_config, cache_dir=None
    )
    assert decorated_get_request_handler(URL_1) == get_request_handler.return_value
    assert decorate_get_request_handler != get_request_handler
