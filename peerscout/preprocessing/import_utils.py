from io import StringIO
import logging
import os

import pandas as pd

from peerscout.utils.collection import force_list, applymap_dict

from ..shared.database_schema import PersonMembership

from .dataNormalisationUtils import normalise_subject_area
from .convertUtils import filter_filenames_by_ext
from .convertUtils import unescape_and_strip_tags_if_not_none

LOGGER = logging.getLogger(__name__)

def get_existing_person_ids(db, include_person_ids):
  return set(x[0] for x in db.session.query(db.person.table.person_id).filter(
    db.person.table.person_id.in_(include_person_ids)
  ).all())

def parse_comma_separated_list(s):
  return [y for y in (x.strip() for x in s.split(',')) if y]

def comma_separated_column_to_map(keys, comma_separated_values):
  return {
    key: parse_comma_separated_list(value_str)
    for key, value_str in zip(keys, comma_separated_values)
  }

def normalise_subject_area_map(subject_area_map):
  return applymap_dict(
    subject_area_map,
    lambda subject_areas: [normalise_subject_area(s) for s in subject_areas]
  )

def dedup_map_values(values_map):
  return applymap_dict(values_map, lambda values: sorted(set(values)))

def xml_decode_person_names(persons_df):
  persons_df['first_name'] = persons_df['first_name'].apply(unescape_and_strip_tags_if_not_none)
  persons_df['last_name'] = persons_df['last_name'].apply(unescape_and_strip_tags_if_not_none)
  return persons_df

def add_or_update_persons_from_dataframe(db, df):
  person_ids = set(df.index.values)
  existing_person_ids = get_existing_person_ids(db, person_ids)
  not_existing_person_ids = person_ids - existing_person_ids
  LOGGER.info(
    "persons, total: %d, existing: %d, not existing: %d",
    len(person_ids), len(existing_person_ids), len(not_existing_person_ids)
  )
  if not not_existing_person_ids:
    LOGGER.info("no new persons to add")
  else:
    not_existing_persons_df = df.loc[not_existing_person_ids]
    if 'is_early_career_researcher' not in not_existing_persons_df:
      not_existing_persons_df['is_early_career_researcher'] = False
    db.person.write_frame(not_existing_persons_df)

def one_to_many_map_to_dataframe(one_to_many_map, fk_name, value_name):
  return pd.DataFrame([
    {fk_name: fk, value_name: value}
    for fk, values in one_to_many_map.items()
    for value in force_list(values)
  ])

def update_one_to_many_table_using_df(db, db_table, df, fk_name, all_keys):
  # Note: we could implement some comparison, but for now just delete and re-insert is good enough
  db_table.delete_where(getattr(db_table.table, fk_name).in_(all_keys))
  db.commit()
  db_table.write_frame(df, index=False)
  db.commit()

def update_one_to_many_map(db, db_table, one_to_many_map, fk_name, value_name):
  df = one_to_many_map_to_dataframe(one_to_many_map, fk_name, value_name)
  update_one_to_many_table_using_df(db, db_table, df, fk_name, one_to_many_map.keys())

def update_person_subject_areas(db, subject_areas_by_person_id):
  LOGGER.debug('updating person subject areas (%d)', len(subject_areas_by_person_id))
  update_one_to_many_map(
    db, db.person_subject_area, subject_areas_by_person_id, 'person_id', 'subject_area'
  )

def update_person_keywords(db, keywords_by_person_id):
  LOGGER.debug('updating person keywords (%d)', len(keywords_by_person_id))
  update_one_to_many_map(
    db, db.person_keyword, keywords_by_person_id, 'person_id', 'keyword'
  )

def update_person_roles(db, roles_by_person_id):
  LOGGER.debug('updating person roles (%d)', len(roles_by_person_id))
  update_one_to_many_map(
    db, db.person_role, roles_by_person_id, 'person_id', 'role'
  )

def update_person_orcids(db, orcid_by_person_id):
  LOGGER.debug('updating person orcids (%d)', len(orcid_by_person_id))
  df = one_to_many_map_to_dataframe(orcid_by_person_id, 'person_id', 'member_id')
  df['member_type'] = PersonMembership.ORCID_MEMBER_TYPE
  update_one_to_many_table_using_df(
    db, db.person_membership, df, 'person_id', orcid_by_person_id.keys()
  )

def find_last_csv_file_in_directory(root_dir, prefix):
  files = sorted([
    fn
    for fn in filter_filenames_by_ext(os.listdir(root_dir), '.csv')
    if fn.startswith(prefix)
  ])
  if not files:
    raise Exception("no csv files found with prefix %s in directory %s" % (prefix, root_dir))
  filename = files[-1]
  return os.path.join(root_dir, filename)

# Unfortunately not everyone seem to be able to encode double quotes in CSV files correctly..
# TODO delete once they know how to
def _hack_double_quote_workaround_find_next_true_quote_end(line, start):
  quote_index = line.find('"', start)
  if quote_index >= 0 and quote_index + 1 < len(line) and line[quote_index + 1] != ',':
    inner_quote_index = line.find('"', quote_index + 1)
    if inner_quote_index < 0:
      return -1
    return _hack_double_quote_workaround_find_next_true_quote_end(line, inner_quote_index + 1)
  return quote_index

def _hack_split_and_fix_double_quote_encoding_issue_in_line(line):
  current_start = 0
  while current_start < len(line):
    if line[current_start] == '"':
      quote_index = _hack_double_quote_workaround_find_next_true_quote_end(line, current_start + 1)
      if quote_index > 0:
        yield '"%s"' % line[current_start + 1:quote_index].replace('"', '""')
        current_start = quote_index + 1
        if current_start < len(line) and line[current_start] == ',':
          current_start += 1
      else:
        yield '"%s"' % line[current_start + 1:].replace('"', '""')
        return
    else:
      sep_index = line.find(',', current_start)
      if sep_index >= 0:
        yield line[current_start:sep_index]
        current_start = sep_index + 1
      else:
        yield line[current_start:]
        return

def hack_fix_double_quote_encoding_issue_in_stream(stream):
  lines = [
    ','.join(_hack_split_and_fix_double_quote_encoding_issue_in_line(line.strip()))
    for line in stream
  ]
  return StringIO('\n'.join(lines))
