import logging

import pandas as pd

from .preprocessingUtils import get_downloads_csv_path

from .import_utils import (
  add_or_update_persons_from_dataframe,
  update_person_subject_areas,
  update_person_keywords,
  update_person_orcids,
  comma_separated_column_to_map,
  normalise_subject_area_map,
  xml_decode_person_names,
  find_last_csv_file_in_directory,
  dedup_map_values
)

from ..shared.database import connect_managed_configured_database

from ..shared.app_config import get_app_config

LOGGER = logging.getLogger(__name__)

class CsvColumns:
  PERSON_ID = 'p_id'
  FIRST_NAME = 'first_nm'
  LAST_NAME = 'last_nm'
  ORCID = 'ORCID'
  FIRST_SUBJECT_AREA = 'First subject area'
  SECOND_SUBJECT_AREA = 'Second subject area'
  KEYWORDS = 'Keywords' # keywords not used

ALL_CSV_COLUMNS = [
  CsvColumns.PERSON_ID, CsvColumns.FIRST_NAME, CsvColumns.LAST_NAME, CsvColumns.ORCID,
  CsvColumns.FIRST_SUBJECT_AREA, CsvColumns.SECOND_SUBJECT_AREA, CsvColumns.KEYWORDS
]

PERSON_CSV_COLUMN_MAPPING = {
  CsvColumns.PERSON_ID: 'person_id',
  CsvColumns.FIRST_NAME: 'first_name',
  CsvColumns.LAST_NAME: 'last_name'
}

KEYWORD_SEPARATOR = '|'


def read_editors_csv(stream):
  return pd.read_csv(stream, skiprows=3, dtype=str)[ALL_CSV_COLUMNS].fillna('')

def to_persons_df(df):
  df = (
    df[sorted(PERSON_CSV_COLUMN_MAPPING.keys())]
    .rename(columns=PERSON_CSV_COLUMN_MAPPING)
    .drop_duplicates()
    .set_index('person_id')
  )
  df['is_early_career_researcher'] = True
  return df

def to_subject_areas_by_person_id_map(df):
  return {
    person_id: sorted(set([first_subject_area, second_subject_area]) - {''})
    for person_id, first_subject_area, second_subject_area in zip(
      df[CsvColumns.PERSON_ID],
      df[CsvColumns.FIRST_SUBJECT_AREA],
      df[CsvColumns.SECOND_SUBJECT_AREA]
    )
  }

def to_keywords_by_person_id_map(df):
  return comma_separated_column_to_map(
    df[CsvColumns.PERSON_ID], df[CsvColumns.KEYWORDS],
    sep=KEYWORD_SEPARATOR
  )

def to_orcid_by_person_id_map(df):
  return comma_separated_column_to_map(df[CsvColumns.PERSON_ID], df[CsvColumns.ORCID])

def update_early_career_researcher_status(db, person_ids):
  LOGGER.debug("updating early career researcher status (%d)", len(person_ids))
  db_table = db['person']

  db.commit()

  db_table.session.query(db_table.table).filter(
    ~db_table.table.person_id.in_(person_ids)
  ).update({
    'is_early_career_researcher': False
  }, synchronize_session=False)

  db_table.session.query(db_table.table).filter(
    db_table.table.person_id.in_(person_ids)
  ).update({
    'is_early_career_researcher': True
  }, synchronize_session=False)

  db.commit()

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
  update_person_orcids(
    db, to_orcid_by_person_id_map(df)
  )
  update_early_career_researcher_status(db, set(df[CsvColumns.PERSON_ID]))

def find_file_to_import():
  app_config = get_app_config()
  prefix = app_config.get('storage', 'ecr_prefix', fallback='')
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
