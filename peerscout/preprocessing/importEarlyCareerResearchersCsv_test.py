from io import StringIO
from contextlib import contextmanager
import logging
from unittest.mock import patch
from configparser import ConfigParser

import pytest

from ..shared.database import populated_in_memory_database

from .import_testing_utils import create_csv_content as _create_csv_content

from . import importEarlyCareerResearchersCsv as import_early_career_researchers_csv_module
from .importEarlyCareerResearchersCsv import (
  import_csv_file_to_database,
  CsvColumns,
  ALL_CSV_COLUMNS,
  find_file_to_import,
  main
)

LOGGER = logging.getLogger(__name__)

FILE_PREFIX = 'file-prefix'

PERSON_ID_1 = 'person1'
PERSON_ID_2 = 'person2'
FIRST_NAME_1 = 'John'
LAST_NAME_1 = 'Smith'
ORCID_1 = 'O-12345'
SUBJECT_AREA_1 = 'Subject Area 1'
SUBJECT_AREA_2 = 'Subject Area 2'

CSV_ITEM_1 = {
  CsvColumns.PERSON_ID: PERSON_ID_1,
  CsvColumns.FIRST_NAME: FIRST_NAME_1,
  CsvColumns.LAST_NAME: LAST_NAME_1,
  CsvColumns.ORCID: ORCID_1,
  CsvColumns.FIRST_SUBJECT_AREA: SUBJECT_AREA_1,
  CsvColumns.SECOND_SUBJECT_AREA: SUBJECT_AREA_2
}

def setup_module():
  logging.basicConfig(level=logging.DEBUG)

@contextmanager
def import_csv(csv_content, dataset=None):
  with populated_in_memory_database(dataset or {}) as db:
    import_csv_file_to_database('test.csv', StringIO(csv_content), db)
    yield db

def create_csv_content(data):
  return _create_csv_content(data, fieldnames=ALL_CSV_COLUMNS)

@pytest.mark.slow
class TestImportCsvFileToDatabase:
  def test_should_import_single_person(self):
    csv_content = create_csv_content([CSV_ITEM_1])
    with import_csv(csv_content) as db:
      df = db.person.read_frame().reset_index()
      LOGGER.debug('df:\n%s', df)
      assert set(zip(df['person_id'], df['is_early_career_researcher'])) == {
        (PERSON_ID_1, True)
      }

  def test_should_update_early_career_researcher_flag_for_existing_person(self):
    csv_content = create_csv_content([{
      **CSV_ITEM_1,
      CsvColumns.PERSON_ID: PERSON_ID_1
    }])
    dataset = {
      'person': [{'person_id': PERSON_ID_1, 'is_early_career_researcher': False}]
    }
    with import_csv(csv_content, dataset) as db:
      df = db.person.read_frame().reset_index()
      LOGGER.debug('df:\n%s', df)
      assert set(zip(df['person_id'], df['is_early_career_researcher'])) == {
        (PERSON_ID_1, True)
      }

  def test_should_clear_no_longer_early_career_researcher_flag(self):
    csv_content = create_csv_content([{
      **CSV_ITEM_1,
      CsvColumns.PERSON_ID: PERSON_ID_1
    }])
    dataset = {
      'person': [{'person_id': PERSON_ID_2, 'is_early_career_researcher': True}]
    }
    with import_csv(csv_content, dataset) as db:
      df = db.person.read_frame().reset_index()
      LOGGER.debug('df:\n%s', df)
      assert set(zip(df['person_id'], df['is_early_career_researcher'])) == {
        (PERSON_ID_1, True),
        (PERSON_ID_2, False)
      }

  def test_should_xml_decode_first_and_last_name(self):
    csv_content = create_csv_content([{
      **CSV_ITEM_1,
      CsvColumns.FIRST_NAME: 'Andr&#x00E9;s',
      CsvColumns.LAST_NAME: 'Andr&#x00E9;s'
    }])
    with import_csv(csv_content) as db:
      df = db.person.read_frame().reset_index()
      LOGGER.debug('df:\n%s', df)
      assert set(zip(df['person_id'], df['first_name'], df['last_name'])) == {
        (PERSON_ID_1, 'Andrés', 'Andrés')
      }

  def test_should_import_empty_subject_area(self):
    csv_content = create_csv_content([{
      **CSV_ITEM_1,
      CsvColumns.FIRST_SUBJECT_AREA: '',
      CsvColumns.SECOND_SUBJECT_AREA: ''
    }])
    with import_csv(csv_content) as db:
      df = db.person.read_frame().reset_index()
      LOGGER.debug('df:\n%s', df)
      assert set(df['person_id']) == set([PERSON_ID_1])
      assert len(db.person_subject_area.read_frame()) == 0

  def test_should_import_multiple_subject_areas(self):
    csv_content = create_csv_content([{
      **CSV_ITEM_1,
      CsvColumns.FIRST_SUBJECT_AREA: SUBJECT_AREA_1,
      CsvColumns.SECOND_SUBJECT_AREA: SUBJECT_AREA_2
    }])
    with import_csv(csv_content) as db:
      df = db.person_subject_area.read_frame().reset_index()
      LOGGER.debug('df:\n%s', df)
      assert set(zip(df['person_id'], df['subject_area'])) == {
        (PERSON_ID_1, SUBJECT_AREA_1),
        (PERSON_ID_1, SUBJECT_AREA_2)
      }

  def test_should_normalise_subject_area(self):
    csv_content = create_csv_content([{
      **CSV_ITEM_1,
      CsvColumns.FIRST_SUBJECT_AREA: 'Science And Matters',
      CsvColumns.SECOND_SUBJECT_AREA: ''
    }])
    with import_csv(csv_content) as db:
      df = db.person_subject_area.read_frame().reset_index()
      LOGGER.debug('df:\n%s', df)
      assert set(zip(df['person_id'], df['subject_area'])) == {
        (PERSON_ID_1, 'Science and Matters')
      }

  def test_should_clear_existing_subject_areas_but_keep_other_persons_subject_areas(self):
    csv_content = create_csv_content([{
      **CSV_ITEM_1,
      CsvColumns.FIRST_SUBJECT_AREA: '',
      CsvColumns.SECOND_SUBJECT_AREA: ''
    }])
    dataset = {
      'person': [{'person_id': PERSON_ID_1}, {'person_id': PERSON_ID_2}],
      'person_subject_area': [
        {'person_id': PERSON_ID_1, 'subject_area': SUBJECT_AREA_1},
        {'person_id': PERSON_ID_2, 'subject_area': SUBJECT_AREA_2}
      ]
    }
    with import_csv(csv_content, dataset) as db:
      df = db.person_subject_area.read_frame().reset_index()
      LOGGER.debug('df:\n%s', df)
      assert set(zip(df['person_id'], df['subject_area'])) == {
        (PERSON_ID_2, SUBJECT_AREA_2)
      }

  def test_should_import_empty_orcid(self):
    csv_content = create_csv_content([{
      **CSV_ITEM_1,
      CsvColumns.ORCID: ''
    }])
    with import_csv(csv_content) as db:
      df = db.person.read_frame().reset_index()
      LOGGER.debug('df:\n%s', df)
      assert set(df['person_id']) == set([PERSON_ID_1])
      assert len(db.person_membership.read_frame()) == 0

  def test_should_import_orcid(self):
    csv_content = create_csv_content([{
      **CSV_ITEM_1,
      CsvColumns.ORCID: ORCID_1
    }])
    with import_csv(csv_content) as db:
      df = db.person_membership.read_frame().reset_index()
      LOGGER.debug('df:\n%s', df)
      assert set(zip(df['person_id'], df['member_type'], df['member_id'])) == {
        (PERSON_ID_1, 'ORCID', ORCID_1)
      }

class TestFindFileToImport:
  def test_should_return_none_if_prefix_configuration_is_missing(self):
    m = import_early_career_researchers_csv_module
    with patch.object(m, 'find_last_csv_file_in_directory'):
      with patch.object(m, 'get_downloads_csv_path'):
        with patch.object(m, 'get_app_config') as get_app_config_mock:

          app_config = ConfigParser()

          get_app_config_mock.return_value = app_config
          assert find_file_to_import() is None

  def test_should_pass_prefix_to_find_last_csv_file_in_directory_mock_and_return_filename(self):
    m = import_early_career_researchers_csv_module
    with patch.object(m, 'find_last_csv_file_in_directory') as \
      find_last_csv_file_in_directory_mock:
      with patch.object(m, 'get_downloads_csv_path') as get_downloads_csv_path_mock:
        with patch.object(m, 'get_app_config') as get_app_config_mock:

          app_config = ConfigParser()
          app_config['storage'] = {'ecr_prefix': FILE_PREFIX}

          get_app_config_mock.return_value = app_config
          assert find_file_to_import() == find_last_csv_file_in_directory_mock.return_value
          find_last_csv_file_in_directory_mock.assert_called_with(
            get_downloads_csv_path_mock.return_value, FILE_PREFIX
          )

class TestMain:
  def test_should_pass_around_values(self):
    m = import_early_career_researchers_csv_module
    with patch.object(m, 'connect_managed_configured_database') as \
      connect_managed_configured_database_mock:
      with patch.object(m, 'find_file_to_import') as find_file_to_import_mock:
        with patch.object(m, 'import_csv_file_to_database') as import_csv_file_to_database_mock:
          with patch.object(m, 'open') as open_mock:
            db = connect_managed_configured_database_mock.return_value.__enter__.return_value
            fp = open_mock.return_value.__enter__.return_value

            main()

            open_mock.assert_called_with(find_file_to_import_mock.return_value, 'r')
            import_csv_file_to_database_mock.assert_called_with(
              find_file_to_import_mock.return_value, fp, db
            )
            db.commit.assert_called()

  def test_should_skip_processing_if_no_file_to_process(self):
    m = import_early_career_researchers_csv_module
    with patch.object(m, 'connect_managed_configured_database'):
      with patch.object(m, 'find_file_to_import') as find_file_to_import_mock:
        with patch.object(m, 'import_csv_file_to_database'):
          with patch.object(m, 'open') as open_mock:
            find_file_to_import_mock.return_value = None

            main()

            open_mock.assert_not_called()
