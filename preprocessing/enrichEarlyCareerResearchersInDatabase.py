import re
from pathlib import Path
import json
from textwrap import shorten

import dateutil
import requests
import pandas as pd
from tqdm import tqdm
import sqlalchemy

from convertUtils import unescape_and_strip_tags_if_not_none, flatten

from preprocessingUtils import get_data_path

from shared_proxy import database

PERSON_ID = 'person_id'

def get(url):
  response = requests.get(url)
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
    # print("filename:", cache_file)
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
    'created_timestamp': parse_datetime_object(item.get('created', None))
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

def enrich_early_career_researchers(db):
  person_table = db.person
  person_membership_table = db.person_membership
  df = pd.DataFrame(
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
    columns=[PERSON_ID, 'first_name', 'last_name', 'ORCID']
  )
  print("number of early career researchers:", len(df))
  print("number of early career researchers with orcid:", sum(pd.notnull(df['ORCID'])))
  cached_get = create_str_cache(
    get,
    cache_dir=get_data_path('cache-http'),
    suffix='.json')
  out_list = []
  pbar = tqdm(df.to_dict(orient='records'))
  for row in pbar:
    person_id = row[PERSON_ID]
    first_name = unescape_and_strip_tags_if_not_none(row['first_name']).strip()
    last_name = unescape_and_strip_tags_if_not_none(row['last_name']).strip()
    full_name = first_name + ' ' + last_name
    pbar.set_description("%40s" % shorten(full_name, width=40))
    orcid = row['ORCID']
    if orcid is not None and len(orcid) > 0:
      # print("orcid:", orcid, first_name, last_name)
      url = (
        "http://api.crossref.org/works?filter=orcid:{}&rows=30&sort=published&order=asc"
        .format(orcid)
      )
      # pbar.set_description("%40s" % shorten(url, width=40))
      response = json.loads(cached_get(url))
      items = [
        extract_manuscript(item)
        for item in response['message']['items']
        if contains_author_with_orcid(item, orcid)
      ]
    else:
      # print("name:", row['first-name'], row['last-name'])
      url = (
        "http://api.crossref.org/works?query.author={}&rows=1000"
        .format(full_name)
      )
      # pbar.set_description("%40s" % shorten(url, width=40))
      response = json.loads(cached_get(url))
      items = [
        extract_manuscript(item)
        for item in response['message']['items']
        if contains_author_with_name(item, first_name, last_name)
      ]
    for item in items:
      out_list.append({
        **item,
        PERSON_ID: person_id
      })

  crossref_dois = set([o.get('doi') for o in out_list])

  manuscript_table = db.manuscript
  existing_dois = set(
    x[0]
    for x in db.session.query(
      manuscript_table.table.doi
    ).filter(
      manuscript_table.table.doi.in_(
        crossref_dois
      )
    ).all()
  )
  new_dois = crossref_dois - existing_dois
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
    'created_timestamp': pd.to_datetime(m.get('created_timestamp'))
  } for m in new_manuscript_info])

  new_manuscript_subject_areas = remove_duplicates(flatten([[{
    'version_id': m.get('version_id'),
    'subject_area': subject_area
  } for subject_area in m.get('subject_areas')] for m in new_manuscript_info]))

  new_manuscript_authors = remove_duplicates([{
    'version_id': m.get('version_id'),
    'person_id': m.get('person_id')
  } for m in new_manuscript_info])

  print("crossref_dois:", len(crossref_dois))
  print("existing_dois:", len(existing_dois))
  print("new_dois:", len(new_dois))
  print("new_manuscript_info:", len(new_manuscript_info))
  print("new_manuscripts:", len(new_manuscripts))
  print("new_manuscript_versions:", len(new_manuscript_versions))
  print("new_manuscript_subject_areas:", len(new_manuscript_subject_areas))
  print("new_manuscript_authors:", len(new_manuscript_authors))
  if len(new_manuscript_info) > 0:
    db.manuscript.create_list(new_manuscripts)
    db.manuscript_version.create_list(new_manuscript_versions)
    db.manuscript_subject_area.create_list(new_manuscript_subject_areas)
    db.manuscript_author.create_list(new_manuscript_authors)
    db.commit()

def main():
  db = database.connect_configured_database()

  enrich_early_career_researchers(db)

  print("Done")

if __name__ == "__main__":
  main()