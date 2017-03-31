from os import listdir
import os

import pandas as pd

from convertUtils import (
  filter_filenames_by_ext,
  unescape_and_strip_tags_if_not_none
)

from preprocessingUtils import get_downloads_csv_path

from shared_proxy import database

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
      'id': person_id,
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
    matching_subject_area = sorted(
      set(matching_df['First subject area'].unique()) |
      set(matching_df['Second subject area'].unique())
    )
    for subject_area in matching_subject_area:
      subject_area = subject_area.strip()
      if len(subject_area) > 0:
        subject_areas.append({
          'person_id': person_id,
          'subject_area': subject_area
        })
  return subject_areas

def add_persons(db, persons):
  person_df = pd.DataFrame(persons).set_index('id')
  # print("person:", person_df)
  print("adding persons")
  db['person'].write_frame(person_df)

def update_subject_areas(db, subject_areas, person_ids):
  subject_area_df = pd.DataFrame(subject_areas)
  # print("subject_area:", subject_area_df)

  print("updating subject areas")
  db_table = db['person_subject_area']
  db_table.delete_where(
    db_table.table.person_id.in_(person_ids)
  )
  db.commit()
  db_table.write_frame(subject_area_df, index=False)

def update_early_career_researcher_status(db, person_ids):
  print("updating early career researcher status")
  db_table = db['person']

  db.commit()

  db_table.session.query(db_table.table).filter(
    ~db_table.table.id.in_(person_ids)
  ).update({
    'is_early_career_researcher': False
  }, synchronize_session=False)

  db_table.session.query(db_table.table).filter(
    db_table.table.id.in_(person_ids)
  ).update({
    'is_early_career_researcher': True
  }, synchronize_session=False)


def convert_xml_file_to(filename, stream, db):
  print("converting:", filename)
  df = (
    pd.read_csv(stream, skiprows=3, dtype={'p_id': str})
    [['p_id', 'first_nm', 'last_nm', 'ORCID', 'First subject area', 'Second subject area']]
  )
  person_ids = set(df['p_id'].values)
  person_table = db['person']
  existing_person_ids = set(x[0] for x in person_table.session.query(person_table.table.id).filter(
    person_table.table.id.in_(person_ids)
  ).all())
  not_existing_person_ids = person_ids - existing_person_ids
  print("total_person_ids:", len(person_ids))
  print("existing_person_ids:", len(existing_person_ids))
  print("not_existing_person_ids:", len(not_existing_person_ids))

  if len(not_existing_person_ids) == 0:
    print("no new persons to add")
  else:
    persons = frame_to_persons(df[
      df['p_id'].isin(not_existing_person_ids)
    ])

    add_persons(db, persons)

  if len(person_ids) == 0:
    print("no persons found")
  else:
    subject_areas = frame_to_subject_areas(df)

    update_subject_areas(db, subject_areas, person_ids)

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
  source = get_downloads_csv_path()

  db = database.connect_configured_database()

  process_file = lambda filename, stream:\
    convert_xml_file_to(filename, stream, db)

  convert_last_csv_files_in_directory(
    source,
    process_file,
    prefix="ejp_query_tool_query_id_380_DataScience:_Early_Career_Researchers"
  )

  db.commit()

  print("Done")

if __name__ == "__main__":
  main()
