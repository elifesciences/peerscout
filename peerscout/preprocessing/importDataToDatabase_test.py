"""
Unit test
"""
import zipfile
import io
import os
from contextlib import contextmanager
import logging

import pytest

from lxml import etree
from lxml.builder import E

from ..shared.database import empty_in_memory_database

from .importDataToDatabase import (
  default_field_mapping_by_table_name,
  convert_zip_file
)

PERSON_ID = 'person_id'
AUTHOR_1_ID = 'author1'

ROLE_1 = 'role1'
ROLE_2 = 'role2'

VERSION_ID1 = '00001-1'

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'test_data')

def setup_module():
  logging.basicConfig(level=logging.DEBUG)
  get_logger().setLevel(logging.DEBUG)

@pytest.fixture(name='logger')
def get_logger():
  return logging.getLogger(__name__)

def zip_for_files(filenames):
  zip_stream = io.BytesIO()

  with zipfile.ZipFile(zip_stream, 'w') as zf:
    for filename in filenames:
      zf.write(os.path.join(TEST_DATA_DIR, filename))

  zip_stream.seek(0)
  return zip_stream

def zip_for_xml(xml_roots):
  zip_stream = io.BytesIO()

  with zipfile.ZipFile(zip_stream, 'w') as zf:
    for i, xml_root in enumerate(xml_roots):
      zf.writestr('%d.xml' % i, etree.tostring(xml_root))

  zip_stream.seek(0)
  return zip_stream

def convert_zip_stream(db, zip_stream):
  field_mapping_by_table_name = default_field_mapping_by_table_name
  early_career_researcher_person_ids = set()

  get_logger().info('zip_stream: %s', zip_stream)
  convert_zip_file(
    'dummy.zip', zip_stream, db, field_mapping_by_table_name,
    early_career_researcher_person_ids
  )

@contextmanager
def empty_database_and_convert_zip_stream(zip_stream):
  with empty_in_memory_database() as db:
    convert_zip_stream(db, zip_stream)
    yield db

def empty_database_and_convert_files(filenames):
  return empty_database_and_convert_zip_stream(zip_for_files(filenames))

def test_regular(logger):
  with empty_database_and_convert_files(['regular-00001.xml']) as db:
    df = db.manuscript_version.read_frame().reset_index()
    logger.debug('df:\n%s', df)
    assert (
      set(df['version_id']) ==
      set([VERSION_ID1])
    )

def test_minimal(logger):
  with empty_database_and_convert_files(['minimal-00001.xml']) as db:
    df = db.manuscript_version.read_frame().reset_index()
    logger.debug('df:\n%s', df)
    assert (
      set(df['version_id']) ==
      set([VERSION_ID1])
    )

def test_with_duplicate_author():
  with empty_database_and_convert_files(['with-duplicate-author-00001.xml']) as db:
    assert (
      set(db.manuscript_author.read_frame()['person_id']) ==
      set(['author1'])
    )

def test_with_duplicate_stage():
  with empty_database_and_convert_files(['with-duplicate-stage-00001.xml']) as db:
    assert (
      set(db.manuscript_stage.read_frame()['triggered_by_person_id']) ==
      set(['reviewer1'])
    )

def test_with_duplicate_stage_and_no_triggered_by_person_id():
  with empty_database_and_convert_files(['with-duplicate-stage-and-no-triggered-by-person-id-00001.xml']) as db:
    # ensure we are inserting a record with None (not a blank string)
    assert (
      set(db.manuscript_stage.read_frame()['triggered_by_person_id']) ==
      set([None])
    )

def test_with_empty_funder_name_ref():
  with empty_database_and_convert_files(['with-empty-funder-name-00001.xml']) as db:
    assert (
      db.manuscript_funding.read_frame().to_dict(orient='records') ==
      [{
        'version_id': VERSION_ID1,
        'funder_name': '',
        'grant_reference_number': 'Funding Reference 1'
      }]
    )
    assert (
      db.manuscript_author_funding.read_frame().to_dict(orient='records') ==
      [{
        'version_id': VERSION_ID1,
        'person_id': 'author1',
        'funder_name': '',
        'grant_reference_number': 'Funding Reference 1'
      }]
    )

def test_with_empty_grant_ref():
  with empty_database_and_convert_files(['with-empty-grant-ref-00001.xml']) as db:
    assert (
      db.manuscript_funding.read_frame().to_dict(orient='records') ==
      [{
        'version_id': VERSION_ID1,
        'funder_name': 'Funder Name 1',
        'grant_reference_number': ''
      }]
    )
    assert (
      db.manuscript_author_funding.read_frame().to_dict(orient='records') ==
      [{
        'version_id': VERSION_ID1,
        'person_id': 'author1',
        'funder_name': 'Funder Name 1',
        'grant_reference_number': ''
      }]
    )

def test_with_unnormalised_subject_area():
  with empty_database_and_convert_files(['with-unnormalised-subject-area-00001.xml']) as db:
    assert (
      set(db.manuscript_subject_area.read_frame()['subject_area']) ==
      set(['Subject Area and Test 1'])
    )

def test_with_missing_persons(logger):
  with empty_database_and_convert_files(['with-missing-persons-00001.xml']) as db:
    df = db.manuscript_version.read_frame().reset_index()
    logger.debug('df:\n%s', df)
    assert (
      set(df['version_id']) ==
      set([VERSION_ID1])
    )

def test_with_manuscript_suffix(logger):
  with empty_database_and_convert_files(['with-manuscript-suffix-00001-suffix.xml']) as db:
    df = db.manuscript_version.read_frame().reset_index()
    logger.debug('df:\n%s', df)
    assert (
      set(df['version_id']) ==
      set([VERSION_ID1])
    )

def test_with_invalid_manuscript_ref(logger):
  with empty_database_and_convert_files(['with-invalid-manuscript-ref.xml']) as db:
    df = db.manuscript_version.read_frame().reset_index()
    logger.debug('df:\n%s', df)
    assert (
      set(df['version_id']) ==
      set(['with-invalid-manuscript-ref-1'])
    )

def test_with_empty_oricid_id(logger):
  with empty_database_and_convert_files(['with-empty-orcid-id.xml']) as db:
    df = db.person.read_frame().reset_index()
    logger.debug('df:\n%s', df)
    assert (
      set(df['person_id']) ==
      set(['author1'])
    )
    df = db.person_membership.read_frame().reset_index()
    logger.debug('df:\n%s', df)
    assert len(df) == 0

def test_with_corresponding_author(logger):
  with empty_database_and_convert_files(['with-corresponding-author.xml']) as db:
    df = db.manuscript_author.read_frame().reset_index().sort_values('seq')
    logger.debug('df:\n%s', df)
    assert (
      [tuple(x) for x in df[['person_id', 'is_corresponding_author']].values] ==
      [('author1', False), ('author2', True)]
    )

def test_should_import_multiple_person_roles(logger):
  xml_root = etree.parse(os.path.join(TEST_DATA_DIR, 'regular-00001.xml')).getroot()
  author1 = xml_root.find(".//person[person-id='%s']" % AUTHOR_1_ID)
  assert author1 is not None
  author1.append(E.roles(
    E.role(E('role-type', ROLE_1)),
    E.role(E('role-type', ROLE_2))
  ))
  get_logger().debug('xml:\n%s', etree.tostring(xml_root, pretty_print=True))
  with empty_database_and_convert_zip_stream(zip_for_xml([xml_root])) as db:
    df = db.person_role.read_frame().reset_index()
    logger.debug('df:\n%s', df)
    assert (
      {*zip(df[PERSON_ID], df['role'])} ==
      {(AUTHOR_1_ID, ROLE_1), (AUTHOR_1_ID, ROLE_2)}
    )
