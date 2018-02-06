from os import listdir
import os
import logging

import pandas as pd

from .convertUtils import (
  filter_filenames_by_ext,
  unescape_and_strip_tags_if_not_none
)

from .preprocessingUtils import get_downloads_csv_path

from .dataNormalisationUtils import normalise_subject_area

from ..shared.database import connect_managed_configured_database

from ..shared.app_config import get_app_config

NAME = 'importEarlyCareerResearchersCsv'

def get_logger():
  return logging.getLogger(NAME)

def null_to_none(x):
  return None if pd.isnull(x) else x

def null_to_none_list(data):
  return [null_to_none(x) for x in data]

def frame_to_persons(df):
  ecr_person_map = (
    df
    [['p_id', 'first_nm', 'last_nm']]
    .drop_duplicates()
    .set_index('p_id', verify_integrity=True)
    .to_dict(orient='index')
  )

  persons = []
  for person_id in ecr_person_map.keys():
    p = ecr_person_map[person_id]
    persons.append({
      'person_id': person_id,
      'first_name': unescape_and_strip_tags_if_not_none(p['first_nm']),
      'last_name': unescape_and_strip_tags_if_not_none(p['last_nm']),
      'status': 'Active',
      'is_early_career_researcher': True
    })
  return persons

def frame_to_subject_areas(df):
  subject_areas = []
  for person_id in df['p_id'].unique():
    matching_df = df[
      df['p_id'] == person_id
    ]
    matching_subject_area = sorted(set([
      normalise_subject_area(subject_area)
      for subject_area in (
        null_to_none_list(matching_df['First subject area']) +
        null_to_none_list(matching_df['Second subject area'])
      )
    ]) - {None})
    for subject_area in matching_subject_area:
      subject_area = subject_area.strip()
      if len(subject_area) > 0:
        subject_areas.append({
          'person_id': person_id,
          'subject_area': normalise_subject_area(subject_area)
        })
  return subject_areas

def frame_to_person_membership(df):
  person_membership = []
  for person_id in df['p_id'].unique():
    matching_df = df[
      df['p_id'] == person_id
    ]
    matching_orcid = sorted(
      set(null_to_none_list(matching_df['ORCID'])) - {None}
    )
    for orcid in matching_orcid:
      orcid = orcid.strip()
      if len(orcid) > 0:
        person_membership.append({
          'person_id': person_id,
          'member_type': 'ORCID',
          'member_id': orcid
        })
  return person_membership

def add_persons(db, persons):
  person_df = pd.DataFrame(persons).set_index('person_id')
  logging.getLogger(NAME).debug("adding persons")
  db['person'].write_frame(person_df)

def update_subject_areas(db, subject_areas, person_ids):
  subject_area_df = pd.DataFrame(subject_areas)

  logging.getLogger(NAME).debug("updating subject areas")
  db_table = db['person_subject_area']
  db_table.delete_where(
    db_table.table.person_id.in_(person_ids)
  )
  db.commit()
  db_table.write_frame(subject_area_df, index=False)

def update_person_membership(db, person_membership, person_ids):
  person_membership_df = pd.DataFrame(person_membership)

  logging.getLogger(NAME).debug("updating person memberships")
  db_table = db['person_membership']
  db_table.delete_where(
    db_table.table.person_id.in_(person_ids)
  )
  db.commit()
  db_table.write_frame(person_membership_df, index=False)

def update_early_career_researcher_status(db, person_ids):
  logging.getLogger(NAME).debug("updating early career researcher status")
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


def convert_csv_file_to(filename, stream, db):
  logger = logging.getLogger(NAME)
  logger.info("converting: %s", filename)
  field_names = [
    'p_id', 'first_nm', 'last_nm', 'ORCID', 'First subject area', 'Second subject area'
  ]
  df = (
    pd.read_csv(stream, skiprows=3, dtype={
      k: str
      for k in field_names
    })
    [field_names]
  )
  person_ids = set(df['p_id'].values)
  person_table = db['person']
  existing_person_ids = set(
    x[0]
    for x in person_table.session.query(person_table.table.person_id).filter(
      person_table.table.person_id.in_(person_ids)
    ).all()
  )
  not_existing_person_ids = person_ids - existing_person_ids
  logger.info("total_person_ids: %d", len(person_ids))
  logger.info("existing_person_ids: %d", len(existing_person_ids))
  logger.info("not_existing_person_ids: %d", len(not_existing_person_ids))

  if len(not_existing_person_ids) == 0:
    logger.info("no new persons to add")
  else:
    persons = frame_to_persons(df[
      df['p_id'].isin(not_existing_person_ids)
    ])

    add_persons(db, persons)

  if len(person_ids) == 0:
    logger.info("no persons found")
  else:
    subject_areas = frame_to_subject_areas(df)
    person_membership = frame_to_person_membership(df)

    update_subject_areas(db, subject_areas, person_ids)
    update_person_membership(db, person_membership, person_ids)

  update_early_career_researcher_status(db, person_ids)

def convert_last_csv_files_in_directory(root_dir, process_file, prefix):
  files = sorted([
    fn
    for fn in filter_filenames_by_ext(listdir(root_dir), '.csv')
    if fn.startswith(prefix)
  ])
  filename = files[-1]
  if filename is not None:
    with open(os.path.join(root_dir, filename), 'rb') as f:
      process_file(filename, f)
  else:
    raise Exception("no csv files found with prefix {} in directory {}".format(prefix, root_dir))

def main():
  app_config = get_app_config()
  ecr_prefix = app_config.get('storage', 'ecr_prefix')
  if not ecr_prefix:
    get_logger().info('ecr_prefix not configured')

  source = get_downloads_csv_path()

  with connect_managed_configured_database() as db:

    process_file = lambda filename, stream:\
      convert_csv_file_to(filename, stream, db)

    convert_last_csv_files_in_directory(
      source,
      process_file,
      prefix=ecr_prefix
    )

    db.commit()

    get_logger().info("Done")

if __name__ == "__main__":
  from ..shared.logging_config import configure_logging
  configure_logging('update')

  main()
