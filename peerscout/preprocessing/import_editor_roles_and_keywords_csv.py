import logging
from io import StringIO

import pandas as pd

from .preprocessingUtils import get_downloads_csv_path

from .import_utils import (
  add_or_update_persons_from_dataframe,
  update_person_subject_areas,
  update_person_keywords,
  update_person_roles,
  comma_separated_column_to_map,
  normalise_subject_area_map,
  dedup_map_values,
  xml_decode_person_names,
  find_last_csv_file_in_directory,
  hack_fix_double_quote_encoding_issue_in_stream
)

from ..shared.database import connect_managed_configured_database

from ..shared.app_config import get_app_config

LOGGER = logging.getLogger(__name__)

class CsvColumns:
  PERSON_ID = 'Person ID'
  FIRST_NAME = 'First Name'
  LAST_NAME = 'Last Name'
  EMAIL = 'Email'
  INSTITUTION = 'Institution'
  ROLE = 'Role'
  SUBJECT_AREAS = 'Subject Areas'
  KEYWORDS = 'Areas of Expertise'

ALL_CSV_COLUMNS = [
  CsvColumns.PERSON_ID, CsvColumns.FIRST_NAME, CsvColumns.LAST_NAME, CsvColumns.EMAIL,
  CsvColumns.INSTITUTION, CsvColumns.ROLE, CsvColumns.SUBJECT_AREAS, CsvColumns.KEYWORDS
]

PERSON_CSV_COLUMN_MAPPING = {
  CsvColumns.PERSON_ID: 'person_id',
  CsvColumns.FIRST_NAME: 'first_name',
  CsvColumns.LAST_NAME: 'last_name',
  CsvColumns.EMAIL: 'email',
  CsvColumns.INSTITUTION: 'institution'
}

def read_editors_csv(stream):
  stream = hack_fix_double_quote_encoding_issue_in_stream(stream)
  return pd.read_csv(stream, skiprows=3, dtype=str)[ALL_CSV_COLUMNS].fillna('')

def to_persons_df(df):
  return (
    df[sorted(PERSON_CSV_COLUMN_MAPPING.keys())]
    .rename(columns=PERSON_CSV_COLUMN_MAPPING)
    .set_index('person_id')
  )

def to_subject_areas_by_person_id_map(df):
  return comma_separated_column_to_map(df[CsvColumns.PERSON_ID], df[CsvColumns.SUBJECT_AREAS])

def to_keywords_by_person_id_map(df):
  return comma_separated_column_to_map(df[CsvColumns.PERSON_ID], df[CsvColumns.KEYWORDS])

def to_roles_by_person_id_map(df):
  return comma_separated_column_to_map(df[CsvColumns.PERSON_ID], df[CsvColumns.ROLE])

def import_csv_file_to_database(filename, stream, db):
  LOGGER.info("converting: %s", filename)
  df = read_editors_csv(stream)
  add_or_update_persons_from_dataframe(
    db, xml_decode_person_names(to_persons_df(df))
  )
  update_person_subject_areas(
    db, normalise_subject_area_map(to_subject_areas_by_person_id_map(df))
  )
  update_person_keywords(
    db, dedup_map_values(to_keywords_by_person_id_map(df))
  )
  db.person_role.delete_all()
  update_person_roles(db, to_roles_by_person_id_map(df))

def find_file_to_import():
  app_config = get_app_config()
  prefix = app_config.get('storage', 'editor_roles_and_keywords_prefix', fallback='')
  if not prefix:
    return None
  return find_last_csv_file_in_directory(get_downloads_csv_path(), prefix)

def main():
  filename = find_file_to_import()
  if not filename:
    LOGGER.info("skipping, no file to process")
    return

  with connect_managed_configured_database() as db:
    with open(filename, 'r') as f:
      import_csv_file_to_database(filename, f, db)

    db.commit()

    LOGGER.info("done")

if __name__ == "__main__":
  from ..shared.logging_config import configure_logging
  configure_logging('update')

  main()
