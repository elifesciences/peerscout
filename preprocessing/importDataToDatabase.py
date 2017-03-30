import itertools
from os.path import basename, splitext
import datetime

import pandas as pd

from convertUtils import (
  process_files_in_directory_or_zip, has_children, parse_xml_file
)

from preprocessingUtils import get_downloads_xml_path

from shared_proxy import database

def auto_convert(name, value):
  if name.endswith('-date'):
    return pd.to_datetime(value)
  return value

DEFAULT_PROPS = {}
DEFAULT_XPATH = ['*']
DEFAULT_EXCLUDE = []

def collect_props(node, props=None, xpaths=None, exclude=None):
  node_props = dict(props or DEFAULT_PROPS)
  if exclude is None:
    exclude = DEFAULT_EXCLUDE
  for xp in xpaths or DEFAULT_XPATH:
    for e in node.findall(xp):
      if not has_children(e) and e.tag not in exclude:
        node_props[e.tag] = auto_convert(e.tag, e.text)
  return node_props

def collect_props_list(nodes, props=None, xpaths=None, exclude=None):
  return [
    collect_props(node, props, xpaths, exclude)
    for node in nodes
  ]

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
    print("unknown_paths:", unknown_paths)

version_copy_paths = {
  'authors': ['authors/author'],
  'editors': ['editors/editor'],
  'senior-editors': ['senior-editors/senior-editor'],
  'referees': ['referees/referee'],
  'potential-editors': ['potential-editors/potential-editor'],
  'potential-referees': ['potential-referees/potential-referee'],
  'manuscript-history': ['history/stage'],
  'keywords': ['keywords/keywords'],
  'author-funding': ['author-funding/author-funding'],
  'manuscript-funding': ['manuscript-funding/manuscript-funding'],
  'subjects': ['subject-areas/subject-area'],
  'related-manuscripts': ['related-manuscripts/related-manuscript'],
  'subject-areas': ['themes/theme']
}

person_copy_paths = {
  'person-dates-not-available': ['dates-not-available/dna'],
  'person-addresses': ['addresses/address'],
  'person-notes': ['notes/note'],
  'person-roles': ['roles/role'],
  'person-memberships': ['memberships/membership']
}

xml_copy_paths = {
  'manuscript/version': version_copy_paths,
  'people/person': person_copy_paths
}

all_version_table_names = [
  'manuscript-versions',
  'emails-meta'
] + [table_name for table_name, xpaths in version_copy_paths.items()]

all_persons_table_names = [
  'persons'
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

def manuscript_number_to_no(x):
  return x.split('-')[-1]

def version_key_to_no(x):
  return 1 + int(x.split('|')[-1])

def convert_xml(doc, db, manuscript_number, export_emails=False):
  for manuscript in doc.findall('manuscript'):
    manuscript_no = manuscript_number_to_no(manuscript_number)
    manuscript_props = collect_props(
      manuscript,
      {
        'manuscript-number': manuscript_number,
        'manuscript-no': manuscript_no
      },
      xpaths=['*', 'production-data/*']
    )
    db.manuscript.update_or_create(id=manuscript_no, data=manuscript_props)
    for version in manuscript.findall('version'):
      version_key = version.find('key').text
      version_no = version_key_to_no(version_key)
      version_manuscript_number = version.find('manuscript-number').text
      version_id = manuscript_no + '-' + str(version_no)

      version_key_props = {
        'manuscript-no': manuscript_no,
        'version-no': version_no,
        'base-manuscript-number': manuscript_number,
        'manuscript-number': version_manuscript_number,
        'version-key': version_key
      }
      version_props = collect_props(version, props={
          **version_key_props
        },
        exclude=known_version_xml_paths.union(set(['key']))
      )

      for table_name, xpaths in version_copy_paths.items():
        version_props[table_name] = collect_props_list(
          itertools.chain.from_iterable([version.findall(xpath) for xpath in xpaths]),
          version_key_props,
          exclude=known_version_xml_paths
        )

      db.manuscript_version.update_or_create(id=version_id, data=version_props)

  for person in doc.findall('people/person'):
    person_key = person.find('person-id').text
    person_props = collect_props(person, exclude=known_person_xml_paths)
    for table_name, xpaths in person_copy_paths.items():
      person_props[table_name] = collect_props_list(
        itertools.chain.from_iterable([
          person.findall(xpath) for xpath in xpaths
        ]),
        exclude=known_person_xml_paths
      )
    db.person.update_or_create(id=person_key, data=person_props)

  # sanity check (to verify that we haven't missed any tags)
  sanity_check_unknown_paths(doc, known_xml_paths)

  db.commit()

def filename_to_manuscript_number(filename):
  return splitext(basename(filename))[0]

def convert_xml_file_contents(filename, stream, db, export_emails):
  current_version = 3
  processed = db.import_processed.get(filename)
  if processed is not None and processed.version == current_version:
    return
  doc = parse_xml_file(stream)
  manuscript_number = filename_to_manuscript_number(filename)
  convert_xml(doc, db, manuscript_number, export_emails=export_emails)
  db.import_processed.update_or_create(
    id=filename,
    when=datetime.datetime.now(),
    version=current_version
  )

def main():

  export_emails = False

  db = database.connect_configured_database()
  db.update_schema()

  process_file = lambda filename, stream:\
    convert_xml_file_contents(filename, stream, db, export_emails=export_emails)

  source = get_downloads_xml_path()

  process_files_in_directory_or_zip(source, process_file, ext=".xml")

  print("done")

if __name__ == "__main__":
  main()
