import logging
import json
from contextlib import contextmanager

import sqlalchemy

from ..shared.database import Database

from .enrichEarlyCareerResearchersInDatabase import (
  extract_manuscript,
  enrich_early_career_researchers,
  get_crossref_works_by_orcid_url,
  get_crossref_works_by_full_name_url
)

TITLE1 = 'Title 1'
ABSTRACT1 = 'Abstract 1'
MANUSCRIPT_TYPE1 = 'Manuscript Type 1'

def setup_module():
  logging.basicConfig(level=logging.DEBUG)

def get_logger():
  return logging.getLogger(__name__)

@contextmanager
def empty_in_memory_database():
  engine = sqlalchemy.create_engine('sqlite://', echo=False)
  get_logger().debug("engine driver: %s", engine.driver)
  db = Database(engine)
  db.update_schema()
  yield db
  db.close()

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

def MapRequestHandler(response_by_url_map):
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

class TestEnrichEarlyCareerResearchers(object):
  def test_should_not_fail_if_database_is_empty(self):
    with empty_in_memory_database() as db:
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
    with empty_in_memory_database() as db:
      db.person.create_list([
        ECR_1
      ])
      db.person_membership.create_list([
        ORCID_MEMBERSHIP_1
      ])
      enrich_early_career_researchers(db, MapRequestHandler(response_by_url_map))

      df = db.manuscript.read_frame().reset_index()
      get_logger().debug('df:\n%s', df)
      assert (
        set(df[DOI]) ==
        {DOI_1}
      )

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
    with empty_in_memory_database() as db:
      db.person.create_list([
        ECR_1
      ])
      # not adding ORCID membership, this will trigger search by name instead
      enrich_early_career_researchers(db, MapRequestHandler(response_by_url_map))

      df = db.manuscript.read_frame().reset_index()
      get_logger().debug('df:\n%s', df)
      assert (
        set(df[DOI]) ==
        {DOI_1}
      )

  def test_should_import_one_if_existing_doi_is_different(self):
    response_by_url_map = {
      get_crossref_works_by_orcid_url(ORCID_1): get_crossref_response([{
        'DOI': DOI_2,
        'author': [{
          'ORCID': ORCID_1
        }]
      }])
    }
    with empty_in_memory_database() as db:
      db.manuscript.create_list([{
        MANUSCRIPT_ID: MANUSCRIPT_ID_1,
        DOI: DOI_1
      }])
      db.person.create_list([
        ECR_1
      ])
      db.person_membership.create_list([
        ORCID_MEMBERSHIP_1
      ])
      enrich_early_career_researchers(db, MapRequestHandler(response_by_url_map))

      df = db.manuscript.read_frame().reset_index()
      get_logger().debug('df:\n%s', df)
      assert (
        set(df[DOI]) ==
        {DOI_1, DOI_2}
      )

  def test_should_not_import_one_if_doi_already_exists(self):
    response_by_url_map = {
      get_crossref_works_by_orcid_url(ORCID_1): get_crossref_response([{
        'DOI': DOI_1,
        'author': [{
          'ORCID': ORCID_1
        }]
      }])
    }
    with empty_in_memory_database() as db:
      db.manuscript.create_list([{
        MANUSCRIPT_ID: MANUSCRIPT_ID_1,
        DOI: DOI_1
      }])
      db.person.create_list([
        ECR_1
      ])
      db.person_membership.create_list([
        ORCID_MEMBERSHIP_1
      ])
      enrich_early_career_researchers(db, MapRequestHandler(response_by_url_map))

      df = db.manuscript.read_frame().reset_index()
      get_logger().debug('df:\n%s', df)
      assert (
        list(df[DOI]) ==
        [DOI_1]
      )

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
    with empty_in_memory_database() as db:
      db.manuscript.create_list([{
        MANUSCRIPT_ID: MANUSCRIPT_ID_1,
        DOI: doi_1_original
      }])
      db.person.create_list([
        ECR_1
      ])
      db.person_membership.create_list([
        ORCID_MEMBERSHIP_1
      ])
      enrich_early_career_researchers(db, MapRequestHandler(response_by_url_map))

      df = db.manuscript.read_frame().reset_index()
      get_logger().debug('df:\n%s', df)
      assert (
        list(df[DOI]) ==
        [doi_1_original]
      )
