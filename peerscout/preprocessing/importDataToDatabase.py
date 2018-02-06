import itertools
from os.path import basename, splitext
import re
import logging

import pandas as pd
from tqdm import tqdm

from .convertUtils import (
  process_files_in_directory_or_zip,
  process_files_in_zip,
  has_children,
  parse_xml_file,
  unescape_and_strip_tags_if_str,
  TableOutput,
  rjust_and_shorten_text
)

from .preprocessingUtils import get_downloads_xml_path

from .dataNormalisationUtils import normalise_subject_area

from ..shared.database import connect_managed_configured_database

NAME = 'importDataToDatabase'

# The data version is similar to the schema version,
# but rather means that the way the data should be interpreted has changed
# (and therefore previously processed files may need to be processed again)
DATA_VERSION = 5

def auto_convert(name, value):
  if name.endswith('-date'):
    return pd.to_datetime(value)
  return value

DEFAULT_PROPS = {}
DEFAULT_XPATH = ['*']
DEFAULT_EXCLUDE = []

def collect_props(
  node,
  props=None,
  xpaths=None,
  exclude=None,
  field_mapping=None,
  transformer_func=None):

  node_props = dict(props or DEFAULT_PROPS)
  if exclude is None:
    exclude = DEFAULT_EXCLUDE
  for xp in xpaths or DEFAULT_XPATH:
    for e in node.findall(xp):
      if (
        not has_children(e) and
        e.tag not in exclude
      ):
        node_props[e.tag] = auto_convert(e.tag, e.text)
  if field_mapping is not None:
    node_props = map_properties(node_props, field_mapping)
  node_props = {
    k: unescape_and_strip_tags_if_str(v)
    for k, v in node_props.items()
  }
  if transformer_func is not None:
    node_props = transformer_func(node_props)
  return node_props

def apply_filter(l, filter_func):
  return l if filter_func is None else [x for x in l if filter_func(x)]

def apply_list_transformer(l, list_transformer_func):
  return l if list_transformer_func is None else list_transformer_func(l)

def collect_props_list(nodes, *args, list_transformer_func=None, **kwargs):
  return apply_list_transformer([
    collect_props(node, *args, **kwargs)
    for node in nodes
  ], list_transformer_func)

def populate_and_append_to_table(table, nodes, *args, list_transformer_func=None, **kwargs):
  for props in collect_props_list(
    nodes, *args, list_transformer_func=list_transformer_func, **kwargs):
    table.append(props)

def find_unknown_paths(doc, known_paths):
  unknown_paths = set()
  for node in doc.findall('*'):
    if node.tag not in known_paths and has_children(node):
      unknown_paths.add(node.tag)
  for known_path in known_paths:
    for node in doc.findall(known_path + '/*'):
      full_path = known_path + '/' + node.tag
      if full_path not in known_paths and has_children(node):
        unknown_paths.add(full_path)
  return unknown_paths

def sanity_check_unknown_paths(doc, known_paths):
  unknown_paths = find_unknown_paths(doc, known_paths)
  if len(unknown_paths) > 0:
    logging.getLogger(NAME).warning("unknown_paths: %s", unknown_paths)

version_copy_paths = {
  'manuscript_author': ['authors/author'],
  'manuscript_editor': ['editors/editor'],
  'manuscript_senior_editor': ['senior-editors/senior-editor'],
  'manuscript_reviewer': ['referees/referee'],
  'manuscript_potential_editor': ['potential-editors/potential-editor'],
  'manuscript_potential_reviewer': ['potential-referees/potential-referee'],
  'manuscript_stage': ['history/stage'],
  'manuscript_keyword': ['keywords/keywords'],
  'manuscript_author_funding': ['author-funding/author-funding'],
  'manuscript_funding': ['manuscript-funding/manuscript-funding'],
  'manuscript_research_organism': ['subject-areas/subject-area'],
  'manuscript_related_manuscript': ['related-manuscripts/related-manuscript'],
  'manuscript_subject_area': ['themes/theme']
}

person_copy_paths = {
  'person_dates_not_available': ['dates-not-available/dna'],
  'person-addresses': ['addresses/address'],
  'person-notes': ['notes/note'],
  'person-roles': ['roles/role'],
  'person_membership': ['memberships/membership']
}

xml_copy_paths = {
  'manuscript/version': version_copy_paths,
  'people/person': person_copy_paths
}

default_field_mapping_by_table_name = {
  'person': {
    'person_id': 'person-id',
    'title': 'title',
    'first_name': 'first-name',
    'middle_name': 'middle_name-name',
    'last_name': 'last-name',
    'status': 'status',
    'email': 'email',
    'institution': 'institution',
    'memberships': 'person-memberships'
  },
  'person_dates_not_available': {
    'person_id': 'person-id',
    'start_date': 'dna-start-date',
    'end_date': 'dna-end-date'
  },
  'person_membership': {
    'person_id': 'person-id',
    'member_type': 'member-type',
    'member_id': 'member-id'
  },
  'manuscript': {
    'manuscript_id': 'manuscript-no',
    'doi': 'production-data-doi',
    'country': 'country'
  },
  'manuscript_version': {
    'version_id': 'version-id',
    'manuscript_id': 'manuscript-no',
    'title': 'title',
    'abstract': 'abstract',
    'manuscript_type': 'manuscript-type',
    'decision': 'decision',
    'decision_timestamp': 'decision-date'
  },
  'manuscript_author': {
    'version_id': 'version-id',
    'person_id': 'author-person-id',
    'seq': 'author-seq',
    'is_corresponding_author': 'is-corr'
  },
  'manuscript_editor': {
    'version_id': 'version-id',
    'person_id': 'editor-person-id'
  },
  'manuscript_senior_editor': {
    'version_id': 'version-id',
    'person_id': 'senior-editor-person-id'
  },
  'manuscript_reviewer': {
    'version_id': 'version-id',
    'person_id': 'referee-person-id'
  },
  'manuscript_potential_editor': {
    'version_id': 'version-id',
    'person_id': 'potential-editor-person-id'
  },
  'manuscript_potential_reviewer': {
    'version_id': 'version-id',
    'person_id': 'potential-referee-person-id',
    'status': 'potential-referee-status',
    'suggested_to_include': 'potential-referee-suggested-to-include',
    'suggested_to_exclude': 'potential-referee-suggested-to-exclude'
  },
  'manuscript_keyword': {
    'version_id': 'version-id',
    'keyword': 'word'
  },
  'manuscript_subject_area': {
    'version_id': 'version-id',
    'subject_area': 'theme'
  },
  'manuscript_research_organism': {
    'version_id': 'version-id',
    'research_organism': 'subject-area'
  },
  'manuscript_stage': {
    'version_id': 'version-id',
    'person_id': 'stage-affective-person-id',
    'triggered_by_person_id': 'stage-triggered-by-person-id',
    'stage_timestamp': 'start-date',
    'stage_name': 'stage-name'
  },
  'manuscript_funding': {
    'version_id': 'version-id',
    'funder_name': 'funding-title',
    'grant_reference_number': 'grant-reference-number'
  },
  'manuscript_author_funding': {
    'version_id': 'version-id',
    'person_id': 'author-person-id',
    'funder_name': 'funding-title',
    'grant_reference_number': 'grant-reference-number'
  }
}

default_filter_by_table_name = {
  'person_membership': lambda x: (
    isinstance(x, dict) and
    len(x.get('member_id', '') or '') > 0
  ),
  'manuscript_keyword': lambda x: (
    isinstance(x, dict) and
    len(x.get('keyword', '')) > 0
  ),
  'manuscript_stage': lambda x: (
    isinstance(x, dict) and
    x.get('person_id') is not None and
    x.get('person_id') != '0'
  )
}

default_transformer_by_table_name = {
  'manuscript_funding': lambda x: ({
    **x,
    'funder_name': x.get('funder_name') or '',
    'grant_reference_number': x.get('grant_reference_number') or ''
  }),
  'manuscript_author_funding': lambda x: ({
    **x,
    'funder_name': x.get('funder_name') or '',
    'grant_reference_number': x.get('grant_reference_number') or ''
  }),
  'manuscript_potential_reviewer': lambda x: ({
    **x,
    'suggested_to_include': x.get('suggested_to_include') == 'yes',
    'suggested_to_exclude': x.get('suggested_to_exclude') == 'yes'
  }),
  'manuscript_subject_area': lambda x: ({
    **x,
    'subject_area': normalise_subject_area(x.get('subject_area'))
  })
}

def filter_duplicate_author_use_highest_corresponding(authors):
  is_corresponding_author_by_person_id = {}
  person_id_used = set()
  filtered_authors = []
  for author in authors:
    person_id = author.get('person_id')
    if author.get('is_corresponding_author') == 'true':
      is_corresponding_author_by_person_id[person_id] = True
    if not person_id in person_id_used:
      person_id_used.add(person_id)
      filtered_authors.append(author)
  return [{
    **author,
    'is_corresponding_author': is_corresponding_author_by_person_id.get(
      author.get('person_id'),
      False
    )
  } for author in filtered_authors]

def filter_duplicate_stage_use_highest_trigger_by_df(df):
  if len(df) < 2:
    return df
  df = df.groupby(
    ['version_id', 'person_id', 'stage_name', 'stage_timestamp']
  ).agg({
    'triggered_by_person_id': lambda l: sorted(l, key=lambda s: s or '')[-1]
  }).reset_index()
  return df

def filter_duplicate_stage_use_highest_trigger_by(stages):
  if len(stages) < 2:
    return stages
  return (
    filter_duplicate_stage_use_highest_trigger_by_df(pd.DataFrame(stages))
    .to_dict(orient='records')
  )

default_list_transformer_by_table_name = {
  'manuscript_author': filter_duplicate_author_use_highest_corresponding,
  # 'manuscript_stage': filter_duplicate_stage_use_highest_trigger_by
}

all_version_table_names = [
  'manuscript_version',
  'emails_meta'
] + [table_name for table_name, xpaths in version_copy_paths.items()]

all_persons_table_names = [
  'person'
] + [table_name for table_name, xpaths in person_copy_paths.items()]

def build_known_xml_paths():
  known_paths = set([
    'manuscript',
    'people',
    'people/person',
    'people/person/address',
    'manuscript/version',
    'manuscript/version/emails',
    'manuscript/version/emails/email',
    'manuscript/production-data'])
  for root_path, copy_paths in xml_copy_paths.items():
    for xpaths in copy_paths.values():
      for xpath in xpaths:
        known_paths.add(root_path + '/' + xpath.split('/')[0])
        known_paths.add(root_path + '/' + xpath)
  return known_paths

known_xml_paths = build_known_xml_paths()

def get_sub_paths(xpaths, prefix):
  return set([xpath.replace(prefix, '') for xpath in xpaths if xpath.startswith(prefix)])

known_version_xml_paths = get_sub_paths(known_xml_paths, 'manuscript/version/')
known_person_xml_paths = get_sub_paths(known_xml_paths, 'people/person/')

def create_combined_list_transformer(table_name):
  def chain_list_transformer(prev_t, next_t):
    if prev_t is None:
      return next_t
    if next_t is None:
      return prev_t
    return lambda l: next_t(prev_t(l))
  list_transformer = None
  filter_func = default_filter_by_table_name.get(table_name)
  item_transformer_func = default_transformer_by_table_name.get(table_name)
  list_transformer_func = default_list_transformer_by_table_name.get(table_name)
  if filter_func is not None:
    list_transformer = lambda l: [x for x in l if filter_func(x)]
  if item_transformer_func is not None:
    list_transformer = chain_list_transformer(
      list_transformer,
      lambda l: map(item_transformer_func, l)
    )
  list_transformer = chain_list_transformer(
    list_transformer,
    list_transformer_func
  )
  return list_transformer

default_combined_list_transformer_by_table_name = {
  k: create_combined_list_transformer(k)
  for k in set(
    default_filter_by_table_name.keys() |
    default_list_transformer_by_table_name.keys() |
    default_transformer_by_table_name.keys()
  )
}

def get_combined_list_transformer(table_name):
  return default_combined_list_transformer_by_table_name.get(table_name)

MANUSCRIPT_NO_REGEX = re.compile(r'^.*-(\d{3,})\D?.*$')

def manuscript_number_to_no(x):
  m = MANUSCRIPT_NO_REGEX.match(x)
  if m:
    return m.group(1)
  else:
    # fallback, return full manuscript reference instead
    return x

def version_key_to_no(x):
  return 1 + int(x.split('|')[-1])

def map_properties(props, field_mapping):
  return {
    k: props[props_key]
    for k, props_key in field_mapping.items()
    if props_key in props
  }

def map_properties_list(props_list, field_mapping):
  return [map_properties(props, field_mapping) for props in props_list]

def remove_duplicates(props_list):
  return [
    props
    for i, props in enumerate(props_list)
    if props not in props_list[i + 1:]
  ]

def update_or_create_record(
  db, table_name, field_mapping, props):

  entity = map_properties(props, field_mapping)
  db[table_name].update_or_create(entity)

def update_or_create_record_if_mapped(
  db, table_name, field_mapping_by_table_name, props):

  if table_name in field_mapping_by_table_name:
    update_or_create_record(db, table_name, field_mapping_by_table_name[table_name], props)

def convert_xml(doc, tables, manuscript_number, field_mapping_by_table_name):
  for manuscript in doc.findall('manuscript'):
    if not 'manuscript' in field_mapping_by_table_name:
      break
    manuscript_no = manuscript_number_to_no(manuscript_number)
    tables['manuscript'].remove_where_property_is(
      'manuscript_id',
      manuscript_no)
    tables['manuscript'].append(collect_props(
      manuscript,
      {
        'manuscript-number': manuscript_number,
        'manuscript-no': manuscript_no
      },
      field_mapping=field_mapping_by_table_name['manuscript'],
      xpaths=['*', 'production-data/*']))
    for version in manuscript.findall('version'):
      version_key = version.find('key').text
      version_no = version_key_to_no(version_key)
      version_id = '{}-{}'.format(manuscript_no, version_no)
      version_manuscript_number = version.find('manuscript-number').text
      for table_name in all_version_table_names:
        if table_name in field_mapping_by_table_name:
          tables[table_name].remove_where_property_is(
            'version_id',
            version_id)
      version_key_props = {
        'manuscript-no': manuscript_no,
        'version-no': version_no,
        'version-id': version_id,
        'base-manuscript-number': manuscript_number,
        'manuscript-number': version_manuscript_number,
        'version-key': version_key
      }
      tables['manuscript_version'].append(collect_props(version, props={
          **version_key_props,
        },
        field_mapping=field_mapping_by_table_name['manuscript_version'],
        exclude=known_version_xml_paths.union(set(['key']))))
      for table_name, xpaths in version_copy_paths.items():
        if table_name in field_mapping_by_table_name:
          populate_and_append_to_table(tables[table_name],
            itertools.chain.from_iterable([version.findall(xpath) for xpath in xpaths]),
            version_key_props,
            field_mapping=field_mapping_by_table_name[table_name],
            # filter_func=default_filter_by_table_name.get(table_name),
            # transformer_func=default_transformer_by_table_name.get(table_name),
            list_transformer_func=get_combined_list_transformer(table_name),
            exclude=known_version_xml_paths)

  for person in doc.findall('people/person'):
    person_key = person.find('person-id').text
    person_key_props = {
      'person-id': person_key
    }
    for table_name in all_persons_table_names:
      tables[table_name].remove_where_property_is(
        'person_id',
        person_key
      )
    tables['person'].append(collect_props(
      person,
      field_mapping=field_mapping_by_table_name['person'],
      exclude=known_person_xml_paths))
    for table_name, xpaths in person_copy_paths.items():
      if table_name in field_mapping_by_table_name:
        populate_and_append_to_table(tables[table_name],
          itertools.chain.from_iterable([person.findall(xpath) for xpath in xpaths]),
          person_key_props,
          field_mapping=field_mapping_by_table_name[table_name],
          list_transformer_func=get_combined_list_transformer(table_name),
          exclude=known_person_xml_paths)

  # sanity check (to verify that we haven't missed any tags)
  sanity_check_unknown_paths(doc, known_xml_paths)

def filename_to_manuscript_number(filename):
  return splitext(basename(filename))[0]

def convert_xml_file_contents(filename, stream, tables, field_mapping_by_table_name):
  doc = parse_xml_file(stream)
  manuscript_number = filename_to_manuscript_number(filename)
  convert_xml(doc, tables, manuscript_number, field_mapping_by_table_name)

def remove_records(db, table_name, df, replace_key):
  if len(df) == 0:
    return
  db.commit()
  db_table = db[table_name]
  if replace_key is not None:
    keys = list(df[replace_key].unique())
    db.commit()
    # print("deleting:", table_name, replace_key, keys, "\n\n")
    db_table.delete_where(
      getattr(db_table.table, replace_key).in_(keys)
    )
    db.commit()

def insert_records(db, table_name, df):
  if len(df) == 0:
    return
  db_table = db[table_name]
  db.commit()
  df = df.drop_duplicates()
  # print("writing data frame:", df, "\n\n")
  db_table.write_frame(df, index=False)

def filter_invalid_person_ids(frame_by_table_name):
  valid_person_ids = set()
  if len(frame_by_table_name['person']) > 0:
    valid_person_ids = set(frame_by_table_name['person']['person_id'].unique())
  for table_name in [
    'manuscript_author',
    'manuscript_author_funding',
    'manuscript_potential_editor',
    'manuscript_potential_reviewer',
    'manuscript_reviewer',
    'manuscript_editor',
    'manuscript_senior_editor',
    'manuscript_stage'
  ]:
    df = frame_by_table_name[table_name]
    if len(df) > 0:
      try:
        frame_by_table_name[table_name] = df[
          df['person_id'].isin(valid_person_ids)
        ]
      except KeyError as e:
        raise Exception('{}: columns({})'.format(table_name, df.columns.values)) from e

def apply_early_career_researcher_flag(
  df, early_career_researcher_person_ids
):
  if len(df) > 0:
    df['is_early_career_researcher'] = df['person_id'].apply(
      lambda person_id: person_id in early_career_researcher_person_ids
    )
  return df

def convert_zip_file(
  zip_filename, zip_stream, db, field_mapping_by_table_name,
  early_career_researcher_person_ids, export_emails=False):

  logger = logging.getLogger(NAME)

  processed = db.import_processed.get(zip_filename)
  if processed is not None and processed.version == DATA_VERSION:
    return

  table_names = set([
    'person',
    'manuscript_email_meta',
    'manuscript',
    'manuscript_version'
  ])
  if export_emails:
    table_names.add('emails')
  for copy_paths in xml_copy_paths.values():
    for table_name in copy_paths.keys():
      table_names.add(table_name)
  tables = dict((table_name, TableOutput(name=table_name)) for table_name in table_names)

  process_file = lambda filename, stream:\
    convert_xml_file_contents(filename, stream, tables, field_mapping_by_table_name)

  process_files_in_zip(zip_stream, process_file, ext=".xml")

  db.session.close_all()

  table_names = ['person', 'manuscript', 'manuscript_version']
  table_names = (
    table_names +
    [t for t in sorted(tables.keys()) if t not in table_names]
  )
  table_names = [t for t in table_names if t in field_mapping_by_table_name]

  # print("table_names:", table_names)
  frame_by_table_name = {
    table_name: tables[table_name].to_frame()
    for table_name in table_names
  }

  frame_by_table_name['person'] = apply_early_career_researcher_flag(
    frame_by_table_name['person'],
    early_career_researcher_person_ids
  )

  frame_by_table_name['manuscript_stage'] = filter_duplicate_stage_use_highest_trigger_by_df(
    frame_by_table_name['manuscript_stage']
  )

  # ignore entries with invalid person id (perhaps address that differently in the future)
  filter_invalid_person_ids(frame_by_table_name)

  # we currently only support update or inserts with a single primary key
  # updating relationships is more complicated,
  # we would need to remove no longer existing relationships for example.
  # removing parents of relationships seem to be costly (tend to have a single primary key),
  # the speed gain of just supporting only those for now is still worth it.
  table_names_supporting_update_or_insert_set = ([
    t for t in table_names if len(db[t].primary_key) == 1
  ])

  table_names_supporting_update_or_insert = [
    t for t in table_names if t in table_names_supporting_update_or_insert_set
  ]

  table_names_not_supporting_update_or_insert = [
    t for t in table_names if t not in table_names_supporting_update_or_insert_set
  ]

  logger.debug('removing records: %s', table_names_not_supporting_update_or_insert)
  pbar = tqdm(list(reversed(table_names_not_supporting_update_or_insert)), leave=False)
  for table_name in pbar:
    pbar.set_description(rjust_and_shorten_text(
      'remove {}'.format(table_name),
      width=40
    ))
    remove_records(db, table_name, frame_by_table_name[table_name], tables[table_name].key)

  logger.debug('updating/creating records: %s', table_names_supporting_update_or_insert)
  pbar = tqdm(table_names_supporting_update_or_insert, leave=False)
  for table_name in pbar:
    df = frame_by_table_name[table_name]
    pbar.set_description(rjust_and_shorten_text(
      'update/insert {}({})'.format(table_name, len(df)),
      width=40
    ))
    if len(df) > 0:
      db[table_name].update_or_create_list(df.to_dict(orient='records'))

  logger.debug('inserting records: %s', table_names_not_supporting_update_or_insert)
  pbar = tqdm(table_names_not_supporting_update_or_insert, leave=False)
  for table_name in pbar:
    df = frame_by_table_name[table_name]
    pbar.set_description(rjust_and_shorten_text(
      'insert {}({})'.format(table_name, len(df)),
      width=40
    ))
    if len(df) > 0:
      insert_records(db, table_name, df)

  logger.debug('marking file as processed: %s (%d)', zip_filename, DATA_VERSION)
  db.import_processed.update_or_create(import_processed_id=zip_filename, version=DATA_VERSION)

  db.commit()

def main():

  field_mapping_by_table_name = default_field_mapping_by_table_name

  with connect_managed_configured_database() as db:

    # keep the early career researcher status
    person_table = db['person']
    early_career_researcher_person_ids = set(
      x[0]
      for x in person_table.session.query(person_table.table.person_id).filter(
        person_table.table.is_early_career_researcher == True # pylint: disable=C0121
      ).all()
    )

    process_zip = lambda filename, stream:\
      convert_zip_file(
        filename, stream, db, field_mapping_by_table_name,
        early_career_researcher_person_ids
      )

    source = get_downloads_xml_path()

    process_files_in_directory_or_zip(source, process_zip, ext=".zip")

    logging.getLogger(NAME).info("done")

if __name__ == "__main__":
  from ..shared.logging_config import configure_logging
  configure_logging('update')

  main()
