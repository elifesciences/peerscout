import itertools
from os.path import basename, splitext

from convertUtils import\
  process_files_in_directory_or_zip, has_children, parse_xml_file, TableOutput, write_tables_to_csv


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

all_version_table_names = [
  'manuscript-versions',
  'emails-meta'
] + [table_name for table_name, xpaths in version_copy_paths.items()]

all_persons_table_names = [
  'persons'
] + [table_name for table_name, xpaths in person_copy_paths.items()]

# keys_by_table_name = {
#   'authors': ['version-key', 'author-person-id'],
#   'editors': ['version-key', 'editor-person-id'],
#   'senior-editors': ['version-key', 'senior-person-id'],
#   'referees': ['version-key', 'referee-person-id'],
#   'potential-editors': ['version-key', 'potential-editor-person-id'],,
#   'potential-referees': ['version-key', 'potential-referee-person-id'],,
#   'manuscript-history': ['version-key', 'stage-name', 'stage-affective-person-id', 'start-date'],
#   'manuscript-keywords': ['version-key', 'editor-person-id'],,
#   'manuscript-author-funding': ['author-funding/author-funding'],
#   'manuscript-funding': ['manuscript-funding/manuscript-funding'],
#   'manuscript-subject-areas': ['subject-areas/subject-area'],
#   'related-manuscripts': ['related-manuscripts/related-manuscript'],
#   'manuscript-themes': ['themes/theme']
# }


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

def convert_xml(doc, tables, manuscript_number):
  export_emails = 'emails' in tables

  for manuscript in doc.findall('manuscript'):
    manuscript_no = manuscript_number_to_no(manuscript_number)
    tables['manuscripts'].append(collect_props(
      manuscript,
      {
        'manuscript-number': manuscript_number,
        'manuscript-no': manuscript_no
      },
      xpaths=['*', 'production-data/*']))
    for version in manuscript.findall('version'):
      version_key = version.find('key').text
      version_no = version_key_to_no(version_key)
      version_manuscript_number = version.find('manuscript-number').text
      for table_name in all_version_table_names:
        tables[table_name].remove_where_property_is('version-key', version_key)
      version_key_props = {
        'manuscript-no': manuscript_no,
        'version-no': version_no,
        'base-manuscript-number': manuscript_number,
        'manuscript-number': version_manuscript_number,
        'version-key': version_key
      }
      tables['manuscript-versions'].append(collect_props(version, props={
          **version_key_props,
          # shortcuts for convenience (will get exported separately as well)
          'keywords': "|".join([ node.text for node in version.findall('keywords/keywords/word') ]),
          'themes': "|".join([ node.text for node in version.findall('themes/theme/theme') ])
        },
        exclude=known_version_xml_paths.union(set(['key']))))
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
        tables['emails'].remove_where_property_is('version-key', version_key)
        populate_and_append_to_table(tables['emails'],
          version.findall('emails/email'),
          version_key_props)

  for person in doc.findall('people/person'):
    person_key = person.find('person-id').text
    person_key_props = {
      'person-id': person_key
    }
    for table_name in all_persons_table_names:
      tables[table_name].remove_where_property_is('person-id', person_key)
    tables['persons'].append(collect_props(person, exclude=known_person_xml_paths))
    for table_name, xpaths in person_copy_paths.items():
      populate_and_append_to_table(tables[table_name],
        itertools.chain.from_iterable([person.findall(xpath) for xpath in xpaths]),
        person_key_props,
        exclude=known_person_xml_paths)

  # sanity check (to verify that we haven't missed any tags)
  sanity_check_unknown_paths(doc, known_xml_paths)

def filename_to_manuscript_number(filename):
  return splitext(basename(filename))[0]

def convert_xml_file_contents(filename, stream, tables):
  doc = parse_xml_file(stream)
  manuscript_number = filename_to_manuscript_number(filename)
  convert_xml(doc, tables, manuscript_number)

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
  tables = dict((table_name, TableOutput(name=table_name)) for table_name in table_names)

  process_file = lambda filename, stream:\
    convert_xml_file_contents(filename, stream, tables)

  # csv_path = "csv-small"
  # source = "../local"

  # csv_path = "../csv"
  # source = "../downloads/ejp_eLife_2000_01_01_00_00_00_2017_01_01_23_59_59.zip"

  csv_path = "../csv"
  source = "../downloads"

  process_files_in_directory_or_zip(source, process_file, ext=".xml")

  write_tables_to_csv(csv_path, tables)

  print("done")

if __name__ == "__main__":
  main()
