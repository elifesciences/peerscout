import csv
import itertools
import xml.etree.ElementTree
from os import listdir, makedirs
from os.path import basename, splitext
from zipfile import ZipFile
from textwrap import shorten

from tqdm import tqdm
import numpy as np

def parse_xml_file(f):
  return xml.etree.ElementTree.parse(f).getroot()

def parse_xml_string(f):
  return xml.etree.ElementTree.fromstring(f)

def has_children(elem):
  return len(list(elem)) > 0

class TableOutput(object):
  def __init__(self):
    self.columns = {}
    self.rows = []

  def append(self, props):
    for k, v in props.items():
      if k not in self.columns:
        self.columns[k] = len(self.columns)
    a = np.empty(len(self.columns), dtype=object)
    for k, v in props.items():
      index = self.columns[k]
      a[index] = v
    self.rows.append(a)

  def header(self):
    a = np.full(len(self.columns), fill_value=None, dtype=object)
    for k, v in self.columns.items():
      a[v] = k
    return a

  def matrix(self):
    column_count = len(self.columns)
    m = np.full((len(self.rows) + 1, column_count), fill_value=None, dtype=object)
    m[0] = self.header()
    for index, row in enumerate(self.rows):
      m[index + 1, :len(row)] = row
    return m

def write_csv(filename, matrix):
  with open(filename, 'w') as csvfile:
    csvwriter = csv.writer(csvfile)
    for row in matrix:
      csvwriter.writerow(row)

def collect_props(node, props = {}, xpaths = ['*'], exclude=[]):
  node_props = dict(props)
  for xp in xpaths:
    for e in node.findall(xp):
      if not has_children(e) and e.tag not in exclude:
        node_props[e.tag] = e.text
  return node_props

def populate_and_append_to_table(table, nodes, props = {}, xpaths = ['*'], exclude=[]):
  for node in nodes:
    table.append(collect_props(node, props, xpaths, exclude))

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
  'manuscript-keywords': ['keywords/keywords'],
  'manuscript-author-funding': ['author-funding/author-funding'],
  'manuscript-funding': ['manuscript-funding/manuscript-funding'],
  'manuscript-subject-areas': ['subject-areas/subject-area'],
  'related-manuscripts': ['related-manuscripts/related-manuscript'],
  'manuscript-themes': ['themes/theme']
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

def convert_xml(doc, tables, manuscript_number):
  export_emails = 'emails' in tables

  for manuscript in doc.findall('manuscript'):
    tables['manuscripts'].append(collect_props(
      manuscript,
      { 'manuscript-number': manuscript_number },
      xpaths=['*', 'production-data/*']))
    for version in manuscript.findall('version'):
      version_key = version.find('key').text
      version_manuscript_number = version.find('manuscript-number').text
      tables['manuscript-versions'].append(collect_props(version, props={
          'base-manuscript-number': manuscript_number,
          # shortcuts for convenience (will get exported separately as well)
          'keywords': "|".join([ node.text for node in version.findall('keywords/keywords/word') ]),
          'themes': "|".join([ node.text for node in version.findall('themes/theme/theme') ])
        },
        exclude=known_version_xml_paths))
      version_key_props = {
        'base-manuscript-number': manuscript_number,
        'manuscript-number': version_manuscript_number,
        'version-key': version_key
      }
      for table_name, xpaths in version_copy_paths.items():
        populate_and_append_to_table(tables[table_name],
          itertools.chain.from_iterable([version.findall(xpath) for xpath in xpaths]),
          version_key_props,
          exclude=known_version_xml_paths)
      for email in version.findall('emails/email'):
        email_props = collect_props(email, version_key_props, exclude=known_version_xml_paths)
        if 'email-message' in email_props:
          del email_props['email-message']
        tables['emails-meta'].append(email_props)
      if export_emails:
        populate_and_append_to_table(tables['emails'],
          version.findall('emails/email'),
          version_key_props)

  for person in doc.findall('people/person'):
    tables['persons'].append(collect_props(person, exclude=known_person_xml_paths))
    person_key = person.find('person-id').text
    person_key_props = {
      'person-key': person_key
    }
    for table_name, xpaths in person_copy_paths.items():
      populate_and_append_to_table(tables[table_name],
        itertools.chain.from_iterable([person.findall(xpath) for xpath in xpaths]),
        person_key_props,
        exclude=known_person_xml_paths)

  # sanity check (to verify that we haven't missed any tags)
  sanity_check_unknown_paths(doc, known_xml_paths)

def filename_to_manuscript_number(filename):
  return splitext(basename(filename))[0]

def convert_xml_files_in_directory(root_dir, tables):
  pbar = tqdm(listdir(root_dir), leave=False)
  for filename in pbar:
    pbar.set_description("%40s" % shorten(filename, width=40))
    f = root_dir + "/" + filename
    doc = parse_xml_file(f)
    manuscript_number = filename_to_manuscript_number(filename)
    convert_xml(doc, tables, manuscript_number)

def convert_xml_files_in_zip(zip_filename, tables):
  with ZipFile(zip_filename) as zip_archive:
    pbar = tqdm(zip_archive.namelist(), leave=False)
    for filename in pbar:
      pbar.set_description("%40s" % shorten(filename, width=40))
      with zip_archive.open(filename) as zip_file:
        doc = parse_xml_string(zip_file.read())
        manuscript_number = filename_to_manuscript_number(filename)
        convert_xml(doc, tables, manuscript_number)
    pbar.set_description("Done")

def write_tables_to_csv(csv_path, tables):
  makedirs(csv_path, exist_ok=True)
  pbar = tqdm(tables.keys(), leave=False)
  for name in pbar:
    pbar.set_description("%40s" % shorten(name, width=40))
    write_csv(csv_path + "/" + name + ".csv", tables[name].matrix())
  pbar.set_description("Done")

def main():

  export_emails = False

  table_names = set([
    'emails-meta',
    'manuscripts',
    'manuscript-versions',
    'persons'
  ])
  if export_emails:
    table_names.add('emails')
  for copy_paths in xml_copy_paths.values():
    for table_name in copy_paths.keys():
      table_names.add(table_name)
  tables = dict((table_name, TableOutput()) for table_name in table_names)

  # csv_path = "csv-small"
  # convert_xml_files_in_directory('../local', tables)

  csv_path = "../csv"
  convert_xml_files_in_zip(
    '../downloads/ejp_eLife_2000_01_01_00_00_00_2017_01_01_23_59_59.zip', tables)

  write_tables_to_csv(csv_path, tables)

  print("done")

if __name__ == "__main__":
  main()
