import zipfile
import io
from io import StringIO
from contextlib import contextmanager
import logging
import csv

import pytest
import sqlalchemy

from shared_proxy import database

from importEarlyCareerResearchersCsv import (
  convert_csv_file_to
)

CSV_FILE_HEADER = 'Query: Xyz\nGenerated on ...\n\n'

PERSON_ID = 'p_id'
FIRST_NAME = 'first_nm'
LAST_NAME = 'last_nm'
ORCID = 'ORCID'
FIRST_SUBJECT_AREA = 'First subject area'
SECOND_SUBJECT_AREA = 'Second subject area'
KEYWORDS = 'Keywords'

FIELD_NAMES = [
  PERSON_ID,
  FIRST_NAME,
  LAST_NAME,
  ORCID,
  FIRST_SUBJECT_AREA,
  SECOND_SUBJECT_AREA,
  KEYWORDS
]

PERSON_ID_1 = 'p1'
FIRST_NAME_1 = 'John'
LAST_NAME_1 = 'Smith'
ORCID_1 = 'O-12345'
SUBJECT_AREA_1 = 'Subject Area 1'
SUBJECT_AREA_2 = 'Subject Area 2'

CSV_ITEM_1 = {
  PERSON_ID: PERSON_ID_1,
  FIRST_NAME: FIRST_NAME_1,
  LAST_NAME: LAST_NAME_1,
  ORCID: ORCID_1,
  FIRST_SUBJECT_AREA: SUBJECT_AREA_1,
  SECOND_SUBJECT_AREA: SUBJECT_AREA_2
}

def setup_module():
  logging.basicConfig(level=logging.DEBUG)

@pytest.fixture(name='logger')
def get_logger():
  return logging.getLogger('test')

@contextmanager
def import_csv(csv_content):
  logger = get_logger()
  logger.debug("csv content:\n%s", csv_content)
  engine = sqlalchemy.create_engine('sqlite://', echo=False)
  logger.debug("engine driver: %s", engine.driver)
  db = database.Database(engine)
  db.update_schema()

  convert_csv_file_to(
    'test.csv', StringIO(csv_content), db
  )
  yield db
  db.close()

def create_csv_content(data):
  get_logger().debug('data: %s', data)
  out = StringIO()
  out.write(CSV_FILE_HEADER)
  writer = csv.DictWriter(out, fieldnames=FIELD_NAMES)
  writer.writeheader()
  writer.writerows(data)
  return out.getvalue()

def test_import_single_line(logger):
  csv_content = create_csv_content([CSV_ITEM_1])
  with import_csv(csv_content) as db:
    df = db.person.read_frame().reset_index()
    logger.debug('df:\n%s', df)
    assert (
      set(df['person_id']) ==
      set([PERSON_ID_1])
    )

def test_import_empty_subject_area(logger):
  csv_content = create_csv_content([{
    **CSV_ITEM_1,
    SECOND_SUBJECT_AREA: ''
  }])
  with import_csv(csv_content) as db:
    df = db.person.read_frame().reset_index()
    logger.debug('df:\n%s', df)
    assert (
      set(df['person_id']) ==
      set([PERSON_ID_1])
    )

def test_import_empty_orcid(logger):
  csv_content = create_csv_content([{
    **CSV_ITEM_1,
    ORCID: ''
  }])
  with import_csv(csv_content) as db:
    df = db.person.read_frame().reset_index()
    logger.debug('df:\n%s', df)
    assert (
      set(df['person_id']) ==
      set([PERSON_ID_1])
    )
