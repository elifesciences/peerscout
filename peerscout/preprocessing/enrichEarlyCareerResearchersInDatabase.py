import re
from pathlib import Path
import json
from textwrap import shorten
import logging

import dateutil
import requests
import pandas as pd
from tqdm import tqdm
import sqlalchemy

from .convertUtils import unescape_and_strip_tags_if_not_none, flatten

from .preprocessingUtils import get_data_path

from ..shared.database import connect_managed_configured_database

PERSON_ID = 'person_id'

def get_logger():
  return logging.getLogger(__name__)

class Columns(object):
  FIRST_NAME = 'first_name'
  LAST_NAME = 'last_name'
  ORCID = 'ORCID'

def get(url):
  response = requests.get(url)
  response.raise_for_status()
  return response.text

def create_cache(f, cache_dir, serializer, deserializer, suffix=''):
  cache_path = Path(cache_dir)
  cache_path.mkdir(exist_ok=True, parents=True)
  clean_pattern = re.compile(r'[^\w]')
  logger = get_logger()

  def clean_fn(fn):
    return clean_pattern.sub('_', fn)

  def cached_f(*args):
    cache_file = cache_path.joinpath(Path(clean_fn(','.join([str(x) for x in args]))).name + suffix)
    logger.debug("filename: %s", cache_file)
    if cache_file.is_file():
      return deserializer(cache_file.read_bytes())
    result = f(*args)
    if not result is None:
      cache_file.write_bytes(serializer(result))
    return result

  return cached_f

def str_serializer(x):
  if isinstance(x, str):
    return x.encode('utf-8')
  return x

def str_deserializer(b):
  return b.decode('utf-8')

def create_str_cache(*args, **kwargs):
  return create_cache(*args, **kwargs, serializer=str_serializer, deserializer=str_deserializer)

def parse_datetime_object(datetime_obj):
  if datetime_obj is None:
    return None
  return dateutil.parser.parse(datetime_obj.get('date-time'))

def extract_manuscript(item):
  return {
    'title': unescape_and_strip_tags_if_not_none(' '.join(item.get('title', []))),
    'abstract': unescape_and_strip_tags_if_not_none(item.get('abstract', None)),
    'doi': item.get('DOI', None),
    'subject_areas': item.get('subject', []),
    'created_timestamp': parse_datetime_object(item.get('created', None)),
    'manuscript_type': unescape_and_strip_tags_if_not_none(item.get('type'))
  }

def contains_author_with_orcid(item, orcid):
  return True in [
    author['ORCID'].endswith(orcid)
    for author in item['author']
    if 'ORCID' in author
  ]

def is_first_name(given_name, first_name):
  return given_name == first_name or given_name.startswith(first_name + ' ')

def contains_author_with_name(item, first_name, last_name):
  return len([
    author
    for author in item.get('author', [])
    if is_first_name(author.get('given', ''), first_name) and
      author.get('family', '') == last_name
  ]) > 0

def remove_duplicates(objs):
  if len(objs) < 2:
    return objs
  return pd.DataFrame(objs).drop_duplicates().to_dict(orient='records')

def get_crossref_works_by_orcid_url(orcid):
  return (
    "http://api.crossref.org/works?filter=orcid:{}&rows=30&sort=published&order=asc"
    .format(orcid)
  )

def get_crossref_works_by_full_name_url(full_name):
  return (
    "http://api.crossref.org/works?query.author={}&rows=1000"
    .format(full_name)
  )

def clean_person_names(person):
  return {
    **person,
    Columns.FIRST_NAME: unescape_and_strip_tags_if_not_none(person[Columns.FIRST_NAME]).strip(),
    Columns.LAST_NAME: unescape_and_strip_tags_if_not_none(person[Columns.LAST_NAME]).strip()
  }

def clean_all_person_names(person_list):
  return [clean_person_names(p) for p in person_list]

def get_early_career_researchers(db):
  person_table = db.person
  person_membership_table = db.person_membership
  return clean_all_person_names(pd.DataFrame(
    db.session.query(
      person_table.table.person_id,
      person_table.table.first_name,
      person_table.table.last_name,
      person_membership_table.table.member_id
    ).outerjoin(
      person_membership_table.table,
      person_membership_table.table.person_id == person_table.table.person_id
    ).filter(
      sqlalchemy.and_(
        person_table.table.is_early_career_researcher == True, # pylint: disable=C0121
        sqlalchemy.or_(
          person_membership_table.table.member_type == None, # pylint: disable=C0121
          person_membership_table.table.member_type == 'ORCID'
        )
      )
    ).all(),
    columns=[PERSON_ID, Columns.FIRST_NAME, Columns.LAST_NAME, Columns.ORCID]
  ).to_dict(orient='records'))

def get_person_full_name(person):
  return ' '.join([person[Columns.FIRST_NAME], person[Columns.LAST_NAME]])

def get_persons_with_orcid(person_list):
  return [p for p in person_list if p[Columns.ORCID]]

def update_progress_with_person(pbar, person):
  pbar.set_description("%40s" % shorten(get_person_full_name(person), width=40))

def get_manuscripts_for_person(person, get_request_handler):
  orcid = person[Columns.ORCID]
  if orcid:
    url = get_crossref_works_by_orcid_url(orcid)
    response = json.loads(get_request_handler(url))
    return [
      extract_manuscript(item)
      for item in response['message']['items']
      if contains_author_with_orcid(item, orcid)
    ]
  else:
    first_name = person[Columns.FIRST_NAME]
    last_name = person[Columns.LAST_NAME]
    full_name = get_person_full_name(person)
    url = get_crossref_works_by_full_name_url(full_name)
    response = json.loads(get_request_handler(url))
    return [
      extract_manuscript(item)
      for item in response['message']['items']
      if contains_author_with_name(item, first_name, last_name)
    ]

def get_person_with_manuscripts_list(person_list, get_request_handler):
  with tqdm(list(person_list), leave=False) as pbar:
    for person in pbar:
      update_progress_with_person(pbar, person)
      manuscripts = get_manuscripts_for_person(person, get_request_handler)
      yield person, manuscripts

def flatten_person_with_manuscripts_list(person_with_manuscripts_list):
  for person, manuscripts in person_with_manuscripts_list:
    person_id = person[PERSON_ID]
    for m in manuscripts:
      yield {
        **m,
        PERSON_ID: person_id
      }

def update_database_with_person_with_manuscripts_list(db, person_with_manuscripts_list):
  out_list = list(flatten_person_with_manuscripts_list(
    person_with_manuscripts_list
  ))

  crossref_dois = set([o.get('doi') for o in out_list])

  manuscript_table = db.manuscript
  existing_dois_lower = {
    x[0] and x[0].lower()
    for x in db.session.query(
      manuscript_table.table.doi
    ).all()
  }
  new_dois = {
    doi
    for doi in crossref_dois
    if doi.lower() not in existing_dois_lower
  }
  new_manuscript_info = [
    {
      **m,
      'manuscript_id': m.get('doi'),
      'version_id': '{}-{}'.format(m.get('doi'), 1),
    }
    for m in out_list
    if m.get('doi') in new_dois
  ]

  new_manuscripts = remove_duplicates([{
    'manuscript_id': m.get('manuscript_id'),
    'doi': m.get('doi')
  } for m in new_manuscript_info])

  new_manuscript_versions = remove_duplicates([{
    'version_id': m.get('version_id'),
    'manuscript_id': m.get('manuscript_id'),
    'title': m.get('title'),
    'abstract': m.get('abstract'),
    'created_timestamp': pd.to_datetime(m.get('created_timestamp')),
    'manuscript_type': m.get('manuscript_type')
  } for m in new_manuscript_info])

  new_manuscript_subject_areas = remove_duplicates(flatten([[{
    'version_id': m.get('version_id'),
    'subject_area': subject_area
  } for subject_area in m.get('subject_areas')] for m in new_manuscript_info]))

  new_manuscript_authors = remove_duplicates([{
    'version_id': m.get('version_id'),
    'person_id': m.get('person_id')
  } for m in new_manuscript_info])

  logger = get_logger()
  logger.debug("crossref_dois: %d", len(crossref_dois))
  logger.debug("existing_dois: %d", len(existing_dois_lower))
  logger.debug("new_dois: %d", len(new_dois))
  logger.debug("new_manuscript_info: %d", len(new_manuscript_info))
  logger.debug("new_manuscripts: %d", len(new_manuscripts))
  logger.debug("new_manuscript_versions: %d", len(new_manuscript_versions))
  logger.debug("new_manuscript_subject_areas: %d", len(new_manuscript_subject_areas))
  logger.debug("new_manuscript_authors: %d", len(new_manuscript_authors))
  if len(new_manuscript_info) > 0:
    db.manuscript.create_list(new_manuscripts)
    db.manuscript_version.create_list(new_manuscript_versions)
    db.manuscript_subject_area.create_list(new_manuscript_subject_areas)
    db.manuscript_author.create_list(new_manuscript_authors)
    db.commit()

def enrich_early_career_researchers(db, get_request_handler):
  logger = get_logger()

  person_list = get_early_career_researchers(db)
  logger.info("number of early career researchers: %d", len(person_list))
  logger.info(
    "number of early career researchers with orcid: %d",
    len(get_persons_with_orcid(person_list))
  )

  person_with_manuscripts_list = get_person_with_manuscripts_list(
    person_list, get_request_handler
  )
  update_database_with_person_with_manuscripts_list(db, person_with_manuscripts_list)

def main():
  with connect_managed_configured_database() as db:
    cached_get = create_str_cache(
      get,
      cache_dir=get_data_path('cache-http'),
      suffix='.json'
    )

    enrich_early_career_researchers(
      db,
      get_request_handler=cached_get
    )

    get_logger().info('done')

if __name__ == "__main__":
  from ..shared.logging_config import configure_logging
  configure_logging('update')

  main()
