import os
import re
from pathlib import Path
import json
import csv
from textwrap import shorten

import requests
import pandas as pd
from tqdm import tqdm

from convertUtils import unescape_and_strip_tags_if_not_none

PERSON_ID = 'person-id'

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

def extract_manuscript(item):
  return {
    'title': unescape_and_strip_tags_if_not_none(' '.join(item.get('title', []))),
    'abstract': unescape_and_strip_tags_if_not_none(item.get('abstract', None)),
    'DOI': item.get('DOI', None),
    'URL': item.get('URL', None),
    'subject-areas': item.get('subject', [])
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

def enrich_early_career_reviewers(csv_path):
  in_filename = os.path.join(csv_path, 'early-career-reviewers.csv')
  out_filename = os.path.join(csv_path, 'crossref-person-extra.csv')
  print("converting:", in_filename)
  df = pd.read_csv(os.path.join(csv_path, 'early-career-reviewers.csv'))
  print("shape:", df.shape)
  cached_get = create_str_cache(
    get,
    cache_dir='../cache-http',
    suffix='.json')
  out_list = []
  pbar = tqdm(df.to_dict(orient='records'))
  for row in pbar:
    person_id = row[PERSON_ID]
    first_name = unescape_and_strip_tags_if_not_none(row['first-name']).strip()
    last_name = unescape_and_strip_tags_if_not_none(row['last-name']).strip()
    full_name = first_name + ' ' + last_name
    pbar.set_description("%40s" % shorten(full_name, width=40))
    orcid = row['ORCID'].strip()
    if len(orcid) > 0:
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
        PERSON_ID: person_id,
        'first-name': first_name,
        'last-name': last_name
      })

  fieldnames = set()
  for out_row in out_list:
    fieldnames |= out_row.keys()
  fieldnames = sorted(fieldnames)
  print("fieldnames:", fieldnames)

  with open(out_filename, 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()

    for out_row in out_list:
      writer.writerow(out_row)

def main():
  csv_path = "../csv"

  enrich_early_career_reviewers(csv_path)

  print("Done")

if __name__ == "__main__":
  main()
