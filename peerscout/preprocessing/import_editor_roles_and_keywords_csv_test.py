from io import StringIO
from contextlib import contextmanager
import logging
from unittest.mock import patch
from configparser import ConfigParser

import pytest

from ..shared.database import populated_in_memory_database

from .import_testing_utils import create_csv_content as _create_csv_content

from . import import_editor_roles_and_keywords_csv as import_editor_roles_and_keywords_csv_module
from .import_editor_roles_and_keywords_csv import (
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
EMAIL_1 = 'john@smith.org'
INSTITUTION_1 = 'Institute of Testing 1'
SUBJECT_AREA_1 = 'Subject Area 1'
SUBJECT_AREA_2 = 'Subject Area 2'
KEYWORD_1 = 'keyword1'
KEYWORD_2 = 'keyword2'

CSV_ITEM_1 = {
  CsvColumns.PERSON_ID: PERSON_ID_1,
  CsvColumns.FIRST_NAME: FIRST_NAME_1,
  CsvColumns.LAST_NAME: LAST_NAME_1,
  CsvColumns.EMAIL: EMAIL_1,
  CsvColumns.INSTITUTION: INSTITUTION_1,
  CsvColumns.SUBJECT_AREAS: SUBJECT_AREA_1,
  CsvColumns.KEYWORDS: KEYWORD_1
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
  def test_should_import_single_line(self):
    csv_content = create_csv_content([CSV_ITEM_1])
    with import_csv(csv_content) as db:
      df = db.person.read_frame().reset_index()
      LOGGER.debug('df:\n%s', df)
      assert set(df['person_id']) == set([PERSON_ID_1])

  def test_should_import_empty_subject_area(self):
    csv_content = create_csv_content([{
      **CSV_ITEM_1,
      CsvColumns.SUBJECT_AREAS: ''
    }])
    with import_csv(csv_content) as db:
      df = db.person.read_frame().reset_index()
      LOGGER.debug('df:\n%s', df)
      assert set(df['person_id']) == set([PERSON_ID_1])
      assert len(db.person_subject_area.read_frame()) == 0

  def test_should_import_multiple_subject_areas(self):
    csv_content = create_csv_content([{
      **CSV_ITEM_1,
      CsvColumns.SUBJECT_AREAS: ', '.join([SUBJECT_AREA_1, SUBJECT_AREA_2])
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
      CsvColumns.SUBJECT_AREAS: 'Science And Matters'
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
      CsvColumns.SUBJECT_AREAS: ''
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

  def test_should_import_multiple_keywords(self):
    csv_content = create_csv_content([{
      **CSV_ITEM_1,
      CsvColumns.KEYWORDS: ', '.join([KEYWORD_1, KEYWORD_2])
    }])
    with import_csv(csv_content) as db:
      df = db.person_keyword.read_frame().reset_index()
      LOGGER.debug('df:\n%s', df)
      assert set(zip(df['person_id'], df['keyword'])) == {
        (PERSON_ID_1, KEYWORD_1),
        (PERSON_ID_1, KEYWORD_2)
      }

  def test_should_import_same_keyword_only_once(self):
    csv_content = create_csv_content([{
      **CSV_ITEM_1,
      CsvColumns.KEYWORDS: ', '.join([KEYWORD_1, KEYWORD_1])
    }])
    with import_csv(csv_content) as db:
      df = db.person_keyword.read_frame().reset_index()
      LOGGER.debug('df:\n%s', df)
      assert set(zip(df['person_id'], df['keyword'])) == {
        (PERSON_ID_1, KEYWORD_1)
      }

  def test_should_tolerate_double_quote_encoding_issues(self):
    csv_content = create_csv_content([{
      **CSV_ITEM_1,
      CsvColumns.KEYWORDS: 'MARKER'
    }]).replace('MARKER', '"some keyword, keyword with "double quotes", other keyword"')
    print(csv_content)
    with import_csv(csv_content) as db:
      df = db.person_keyword.read_frame().reset_index()
      LOGGER.debug('df:\n%s', df)
      print(df)
      assert set(zip(df['person_id'], df['keyword'])) == {
        (PERSON_ID_1, 'some keyword'),
        (PERSON_ID_1, 'keyword with "double quotes"'),
        (PERSON_ID_1, 'other keyword')
      }

  def test_should_clear_existing_keywords_but_keep_other_persons_keywords(self):
    csv_content = create_csv_content([{
      **CSV_ITEM_1,
      CsvColumns.KEYWORDS: ''
    }])
    dataset = {
      'person': [{'person_id': PERSON_ID_1}, {'person_id': PERSON_ID_2}],
      'person_keyword': [
        {'person_id': PERSON_ID_1, 'keyword': KEYWORD_1},
        {'person_id': PERSON_ID_2, 'keyword': KEYWORD_2}
      ]
    }
    with import_csv(csv_content, dataset) as db:
      df = db.person_keyword.read_frame().reset_index()
      LOGGER.debug('df:\n%s', df)
      assert set(zip(df['person_id'], df['keyword'])) == {
        (PERSON_ID_2, KEYWORD_2)
      }

class TestFindFileToImport:
  def test_should_return_none_if_prefix_configuration_is_missing(self):
    m = import_editor_roles_and_keywords_csv_module
    with patch.object(m, 'find_last_csv_file_in_directory'):
      with patch.object(m, 'get_downloads_csv_path'):
        with patch.object(m, 'get_app_config') as get_app_config_mock:

          app_config = ConfigParser()

          get_app_config_mock.return_value = app_config
          assert find_file_to_import() is None

  def test_should_pass_prefix_to_find_last_csv_file_in_directory_mock_and_return_filename(self):
    m = import_editor_roles_and_keywords_csv_module
    with patch.object(m, 'find_last_csv_file_in_directory') as \
      find_last_csv_file_in_directory_mock:
      with patch.object(m, 'get_downloads_csv_path') as get_downloads_csv_path_mock:
        with patch.object(m, 'get_app_config') as get_app_config_mock:

          app_config = ConfigParser()
          app_config['storage'] = {'editor_roles_and_keywords_prefix': FILE_PREFIX}

          get_app_config_mock.return_value = app_config
          assert find_file_to_import() == find_last_csv_file_in_directory_mock.return_value
          find_last_csv_file_in_directory_mock.assert_called_with(
            get_downloads_csv_path_mock.return_value, FILE_PREFIX
          )

class TestMain:
  def test_should_pass_around_values(self):
    m = import_editor_roles_and_keywords_csv_module
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
    m = import_editor_roles_and_keywords_csv_module
    with patch.object(m, 'connect_managed_configured_database'):
      with patch.object(m, 'find_file_to_import') as find_file_to_import_mock:
        with patch.object(m, 'import_csv_file_to_database'):
          with patch.object(m, 'open') as open_mock:
            find_file_to_import_mock.return_value = None

            main()

            open_mock.assert_not_called()
