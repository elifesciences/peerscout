import re
from pathlib import Path
import json
import logging
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from configparser import ConfigParser
from typing import List, Dict, Any

import dateutil
import requests
import pandas as pd
import sqlalchemy
from ratelimit import rate_limited

from peerscout.utils.collection import parse_list
from peerscout.utils.tqdm import tqdm
from peerscout.utils.requests import configure_session_retry
from peerscout.utils.threading import lazy_thread_local

from .convertUtils import unescape_and_strip_tags_if_not_none, flatten

from .preprocessingUtils import get_data_path

from ..shared.database import connect_managed_configured_database
from ..shared.app_config import get_app_config

LOGGER = logging.getLogger(__name__)

PERSON_ID = 'person_id'

DEFAULT_MAX_WORKERS = 10

DEFAULT_RATE_LIMIT_COUNT = 50
DEFAULT_RATE_LIMIT_INTERVAL_SEC = 1

DEFAULT_MAX_RETRY = 10

DEFAULT_RETRY_ON_STATUS_CODES = [429, 500, 502, 503, 504]

Person = Dict[str, Any]
PersonList = List[Person]

ENRICH_DATA_CONFIG_SECTION = 'enrich-data'

class Columns:
  FIRST_NAME = 'first_name'
  LAST_NAME = 'last_name'
  ORCID = 'ORCID'

def get(url, session=None):
  LOGGER.debug('requesting: %s', url)
  response = (session or requests).get(url)
  LOGGER.debug('response received: %s (%s)', url, response.status_code)
  response.raise_for_status()
  return response.text

def create_cache(f, cache_dir, serializer, deserializer, suffix=''):
  cache_path = Path(cache_dir)
  cache_path.mkdir(exist_ok=True, parents=True)
  clean_pattern = re.compile(r'[^\w]')

  def clean_fn(fn):
    return clean_pattern.sub('_', fn)

  def cached_f(*args):
    cache_file = cache_path.joinpath(Path(clean_fn(','.join([str(x) for x in args]))).name + suffix)
    LOGGER.debug("filename: %s", cache_file)
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
    for author in item.get('author', [])
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

def clean_person_names(person: Person):
  return {
    **person,
    Columns.FIRST_NAME: unescape_and_strip_tags_if_not_none(person[Columns.FIRST_NAME]).strip(),
    Columns.LAST_NAME: unescape_and_strip_tags_if_not_none(person[Columns.LAST_NAME]).strip()
  }

def clean_all_person_names(person_list: PersonList):
  return [clean_person_names(p) for p in person_list]

def get_persons_to_enrich(db, include_early_career_researchers=False, include_roles=None) \
  -> PersonList:

  if not include_early_career_researchers and not include_roles:
    raise AssertionError('early_career_researchers or roles required')
  person_table = db.person
  person_membership_table = db.person_membership
  query = db.session.query(
    person_table.table.person_id,
    person_table.table.first_name,
    person_table.table.last_name,
    person_membership_table.table.member_id
  ).outerjoin(
    db.person_role.table,
    db.person_role.table.person_id == person_table.table.person_id
  ).outerjoin(
    person_membership_table.table,
    person_membership_table.table.person_id == person_table.table.person_id
  ).filter(
    sqlalchemy.or_(
      person_membership_table.table.member_type == None, # pylint: disable=C0121
      person_membership_table.table.member_type == 'ORCID'
    )
  )

  conditions = []
  if include_early_career_researchers:
    conditions.append(
      person_table.table.is_early_career_researcher == True # pylint: disable=C0121
    )
  if include_roles:
    conditions.append(
      db.person_role.table.role.in_(include_roles)
    )
  query = query.filter(sqlalchemy.or_(*conditions))

  return clean_all_person_names(pd.DataFrame(
    query.distinct().all(),
    columns=[PERSON_ID, Columns.FIRST_NAME, Columns.LAST_NAME, Columns.ORCID]
  ).to_dict(orient='records'))

def get_person_full_name(person: Person):
  return ' '.join([person[Columns.FIRST_NAME], person[Columns.LAST_NAME]])

def get_persons_with_orcid(person_list: PersonList):
  return [p for p in person_list if p[Columns.ORCID]]

def get_manuscripts_for_person(person: Person, get_request_handler):
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

def tqdm_parallel_map_unordered(executor, fn, iterable, **kwargs):
  futures_list = [executor.submit(fn, item) for item in iterable]
  yield from (
    f.result()
    for f in tqdm(concurrent.futures.as_completed(futures_list), total=len(futures_list), **kwargs)
  )

def get_enriched_person_with_manuscripts_list(
  person_list: PersonList, get_request_handler, max_workers=1):

  with ThreadPoolExecutor(max_workers=max_workers) as executor:
    yield from tqdm_parallel_map_unordered(
      executor,
      lambda person: (person, get_manuscripts_for_person(person, get_request_handler)),
      person_list
    )

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
    'manuscript_type': m.get('manuscript_type'),
    'is_published': True
  } for m in new_manuscript_info])

  new_manuscript_subject_areas = remove_duplicates(flatten([[{
    'version_id': m.get('version_id'),
    'subject_area': subject_area
  } for subject_area in m.get('subject_areas')] for m in new_manuscript_info]))

  new_manuscript_authors = remove_duplicates([{
    'version_id': m.get('version_id'),
    'person_id': m.get('person_id')
  } for m in new_manuscript_info])

  LOGGER.debug("crossref_dois: %d", len(crossref_dois))
  LOGGER.debug("existing_dois: %d", len(existing_dois_lower))
  LOGGER.debug("new_dois: %d", len(new_dois))
  LOGGER.debug("new_manuscript_info: %d", len(new_manuscript_info))
  LOGGER.debug("new_manuscripts: %d", len(new_manuscripts))
  LOGGER.debug("new_manuscript_versions: %d", len(new_manuscript_versions))
  LOGGER.debug("new_manuscript_subject_areas: %d", len(new_manuscript_subject_areas))
  LOGGER.debug("new_manuscript_authors: %d", len(new_manuscript_authors))
  if len(new_manuscript_info) > 0:
    db.manuscript.create_list(new_manuscripts)
    db.manuscript_version.create_list(new_manuscript_versions)
    db.manuscript_subject_area.create_list(new_manuscript_subject_areas)
    db.manuscript_author.create_list(new_manuscript_authors)
    db.commit()

def enrich_and_update_person_list(
  db, person_list: PersonList, get_request_handler, max_workers=1):

  LOGGER.info("number of persons: %d", len(person_list))
  LOGGER.info("number of persons with orcid: %d", len(get_persons_with_orcid(person_list)))

  person_with_manuscripts_list = get_enriched_person_with_manuscripts_list(
    person_list, get_request_handler, max_workers=max_workers
  )
  update_database_with_person_with_manuscripts_list(db, person_with_manuscripts_list)

def get_configured_include_early_career_researcher(app_config: ConfigParser):
  return app_config.getboolean(
    ENRICH_DATA_CONFIG_SECTION, 'include_early_career_researcher', fallback=False
  )

def get_configured_include_roles(app_config: ConfigParser):
  return parse_list(app_config.get(
    ENRICH_DATA_CONFIG_SECTION, 'include_roles', fallback='')
  )

def get_configured_max_workers(app_config):
  return app_config.getint('pipeline', 'max_workers', fallback=DEFAULT_MAX_WORKERS)

def get_configured_rate_limit_and_interval_sec(app_config):
  return (
    app_config.getint(
      'crossref', 'rate_limit_count', fallback=DEFAULT_RATE_LIMIT_COUNT
    ),
    app_config.getint(
      'crossref', 'rate_limit_interval_sec', fallback=DEFAULT_RATE_LIMIT_INTERVAL_SEC
    )
  )

def get_configured_max_retries(app_config: ConfigParser):
  return app_config.getint('crossref', 'max_retries', fallback=DEFAULT_MAX_RETRY)

def parse_int_list(s, default_value=None):
  if s:
    return [int(x.strip()) for x in s.split(',')]
  return default_value

def get_configured_retry_on_status_codes(app_config):
  return parse_int_list(
    app_config.get('crossref', 'retry_on_status_codes', fallback=None),
    DEFAULT_RETRY_ON_STATUS_CODES
  )

def get_session_with_retry(**kwargs):
  session = requests.Session()
  configure_session_retry(session, **kwargs)
  return session

def decorate_get_request_handler(get_request_handler, app_config, cache_dir=None):
  # Note: could also get this from the Crossref API itself
  #   (via X-Rate-Limit-Limit and X-Rate-Limit-Interval)
  rate_limit_count, rate_limit_interval_sec = (
    get_configured_rate_limit_and_interval_sec(app_config)
  )
  LOGGER.info('using rate limit: %d / %ds', rate_limit_count, rate_limit_interval_sec)

  max_retries = get_configured_max_retries(app_config)
  retry_on_status_codes = get_configured_retry_on_status_codes(app_config)
  LOGGER.info(
    'using max_retries: %d (status codes: %s)', max_retries, retry_on_status_codes
  )

  get_session = lazy_thread_local(lambda: get_session_with_retry(
    max_retries=max_retries,
    status_forcelist=retry_on_status_codes
  ))
  get_with_retry = lambda url: get_request_handler(url, session=get_session())
  rate_limited_get = rate_limited(rate_limit_count, rate_limit_interval_sec)(
    get_with_retry
  )

  if cache_dir:
    return create_str_cache(
      rate_limited_get,
      cache_dir=cache_dir,
      suffix='.json'
    )
  else:
    return rate_limited_get

def main():
  app_config = get_app_config()

  include_early_career_researchers = get_configured_include_early_career_researcher(app_config)
  include_roles = get_configured_include_roles(app_config)

  max_workers = get_configured_max_workers(app_config)
  LOGGER.info('using max_workers: %d', max_workers)

  get_request_handler = decorate_get_request_handler(
    get,
    app_config,
    cache_dir=get_data_path('cache-http'),
  )

  with connect_managed_configured_database() as db:
    person_list = get_persons_to_enrich(
      db,
      include_early_career_researchers=include_early_career_researchers,
      include_roles=include_roles
    )
    LOGGER.info(
      'person list: %d (include ecr: %s, roles: %s)',
      len(person_list), include_early_career_researchers, include_roles
    )
    enrich_and_update_person_list(
      db,
      person_list,
      get_request_handler=get_request_handler,
      max_workers=max_workers
    )

    LOGGER.info('done')

if __name__ == "__main__":
  from ..shared.logging_config import configure_logging
  configure_logging('update')

  main()
