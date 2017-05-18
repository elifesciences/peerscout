"""
Unit test
"""
import zipfile
import io
from contextlib import contextmanager
import logging

import sqlalchemy

from shared_proxy import database

from importDataToDatabase import (
  default_field_mapping_by_table_name,
  convert_zip_file
)

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger('test')

VERSION_ID1 = '00001-1'

@contextmanager
def convert_files(filenames):
  engine = sqlalchemy.create_engine('sqlite://', echo=False)
  logger.debug("engine driver: %s", engine.driver)
  db = database.Database(engine)
  db.update_schema()

  zip_filename = 'dummy.zip'
  zip_stream = io.BytesIO()

  with zipfile.ZipFile(zip_stream, 'w') as zf:
    for filename in filenames:
      zf.write("test_data/" + filename)

  zip_stream.seek(0)

  field_mapping_by_table_name = default_field_mapping_by_table_name
  early_career_researcher_person_ids = set()

  convert_zip_file(
    zip_filename, zip_stream, db, field_mapping_by_table_name,
    early_career_researcher_person_ids
  )
  yield db
  db.close()

def test_regular():
  with convert_files(['regular-00001.xml']) as db:
    df = db.manuscript_version.read_frame().reset_index()
    logger.debug('df:\n%s', df)
    assert (
      set(df['version_id']) ==
      set([VERSION_ID1])
    )

def test_minimal():
  with convert_files(['minimal-00001.xml']) as db:
    df = db.manuscript_version.read_frame().reset_index()
    logger.debug('df:\n%s', df)
    assert (
      set(df['version_id']) ==
      set([VERSION_ID1])
    )

def test_with_duplicate_author():
  with convert_files(['with-duplicate-author-00001.xml']) as db:
    assert (
      set(db.manuscript_author.read_frame()['person_id']) ==
      set(['author1'])
    )

def test_with_duplicate_stage():
  with convert_files(['with-duplicate-stage-00001.xml']) as db:
    assert (
      set(db.manuscript_stage.read_frame()['triggered_by_person_id']) ==
      set(['reviewer1'])
    )

def test_with_duplicate_stage_and_no_triggered_by_person_id():
  with convert_files(['with-duplicate-stage-and-no-triggered-by-person-id-00001.xml']) as db:
    # ensure we are inserting a record with None (not a blank string)
    assert (
      set(db.manuscript_stage.read_frame()['triggered_by_person_id']) ==
      set([None])
    )

def test_with_empty_funder_name_ref():
  with convert_files(['with-empty-funder-name-00001.xml']) as db:
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
  with convert_files(['with-empty-grant-ref-00001.xml']) as db:
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
  with convert_files(['with-unnormalised-subject-area-00001.xml']) as db:
    assert (
      set(db.manuscript_subject_area.read_frame()['subject_area']) ==
      set(['Subject Area and Test 1'])
    )

def test_with_missing_persons():
  with convert_files(['with-missing-persons-00001.xml']) as db:
    df = db.manuscript_version.read_frame().reset_index()
    logger.debug('df:\n%s', df)
    assert (
      set(df['version_id']) ==
      set([VERSION_ID1])
    )

def test_with_manuscript_suffix():
  with convert_files(['with-manuscript-suffix-00001-suffix.xml']) as db:
    df = db.manuscript_version.read_frame().reset_index()
    logger.debug('df:\n%s', df)
    assert (
      set(df['version_id']) ==
      set([VERSION_ID1])
    )

def test_with_invalid_manuscript_ref():
  with convert_files(['with-invalid-manuscript-ref.xml']) as db:
    df = db.manuscript_version.read_frame().reset_index()
    logger.debug('df:\n%s', df)
    assert (
      set(df['version_id']) ==
      set(['with-invalid-manuscript-ref-1'])
    )
