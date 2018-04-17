import csv
import itertools
import xml.etree.ElementTree
from os import listdir, makedirs
from os.path import basename, splitext, isfile
import os
from zipfile import ZipFile
import html
from html.parser import HTMLParser
import logging

import numpy as np
import pandas as pd

from peerscout.utils.tqdm import tqdm

NAME = 'convertUtils'

class MLStripper(HTMLParser):
  def __init__(self):
    super().__init__()
    self.reset()
    self.strict = False
    self.convert_charrefs = True
    self.fed = []

  def handle_data(self, d):
    self.fed.append(d)

  def get_data(self):
    return ''.join(self.fed)

  def error(self, err):
    raise err

def strip_tags(text):
  s = MLStripper()
  s.feed(text)
  return s.get_data()

def unescape_and_strip_tags(text):
  return strip_tags(html.unescape(text))

def unescape_and_strip_tags_if_not_none(text):
  return unescape_and_strip_tags(text) if text else None

def unescape_and_strip_tags_if_str(x):
  return unescape_and_strip_tags(x) if isinstance(x, str) else x

flatten = lambda l: [item for sublist in l for item in sublist]

shorten_text = lambda s, width, placeholder='..': (
  s
  if len(s) <= width
  else s[:width - len(placeholder)] + placeholder
)

rjust_and_shorten_text = lambda s, width, placeholder='..': (
  shorten_text(s, width, placeholder)
  if len(s) > width
  else s.rjust(width)
)

debugv_enabled = False

def debugv(*args):
  if debugv_enabled:
    logging.getLogger(NAME).debug(*args)

def groupby_to_dict(l, kf, vf):
  return {
    k: vf(list(v))
    for k, v in itertools.groupby(l, kf)
  }

def parse_xml_file(f):
  return xml.etree.ElementTree.parse(f).getroot()

def parse_xml_string(f):
  return xml.etree.ElementTree.fromstring(f)

def has_children(elem):
  return len(list(elem)) > 0


class TableOutput(object):
  def __init__(self, name=None, key=None, sort_by=None):
    self.name = name
    self.columns = {}
    self.rows = []
    self.key = key
    self.sort_by = sort_by
    if key:
      self.set_index(key)
    self.rows_by_key = {}
    self.logger = logging.getLogger(NAME)

  def __repr__(self):
    return '%s(name=%s, columns=%s, n_rows=%d)' % (
      type(self).__name__, self.name, self.columns, len(self.rows)
    )

  def append(self, props):
    for k, v in props.items():
      if k not in self.columns:
        self.columns[k] = len(self.columns)
    a = np.empty(len(self.columns), dtype=object)
    for k, v in props.items():
      index = self.columns[k]
      a[index] = v
    if self.key:
      debugv(
        "adding: %s, %s, %s, %d",
        self.name, self.key, props[self.key], len(self.rows_by_key)
      )
      self.rows_by_key.setdefault(props[self.key], []).append(a)
      debugv(
        "added: %s, %s, %s, %d",
        self.name, self.key, props[self.key], len(self.rows_by_key)
      )
    else:
      self.rows.append(a)

  def set_index(self, key):
    if self.key != key:
      debugv("setting index to: %s, %s", self.name, key)
      if not key:
        self.rows = flatten(self.rows_by_key.values())
        self.rows_by_key = {}
        self.key = key
      else:
        self.set_index(None)
        self.key = key
        self.rows_by_key = groupby_to_dict(
          self.rows, lambda row: row[self.columns[key]], lambda row: row)
        self.rows = []

  def remove_where_property_is(self, col, value):
    self.set_index(col)
    if value in self.rows_by_key:
      debugv("removing: %s, %s, %s", self.name, self.key, value)
      del self.rows_by_key[value]
    # self.remove_where(condition=lambda row: row[self.columns[prop]] == value)

  def header(self):
    a = np.full(len(self.columns), fill_value=None, dtype=object)
    for k, v in self.columns.items():
      a[v] = k
    return a

  def to_frame(self):
    m = self.matrix()
    return pd.DataFrame(m[1:], columns=m[0])

  def matrix(self):
    column_count = len(self.columns)
    if self.key:
      rows = flatten(self.rows_by_key.values())
      debugv(
        "rows after flattening: %s, %s, %d, %d",
        self.name, self.key, len(rows), len(self.rows_by_key)
      )
    else:
      rows = self.rows
    m = np.full((len(rows) + 1, column_count), fill_value=None, dtype=object)
    m[0] = self.header()
    for index, row in enumerate(rows):
      m[index + 1, :len(row)] = row
    return m


def write_csv(filename, matrix):
  with open(filename, 'w') as csvfile:
    csvwriter = csv.writer(csvfile)
    for row in matrix:
      csvwriter.writerow(row)

def write_pickle(filename, matrix):
  columns = matrix[0]
  df = pd.DataFrame(matrix[1:], columns=columns)
  for c in columns:
    if c.endswith('-date'):
      df[c] = pd.to_datetime(df[c])
  df.to_pickle(filename)

def write_tables_to_csv(csv_path, tables, pickle=False):
  makedirs(csv_path, exist_ok=True)
  pbar = tqdm(tables.keys(), leave=False)
  for name in pbar:
    pbar.set_description(rjust_and_shorten_text(name, width=40))
    write_csv(csv_path + "/" + name + ".csv", tables[name].matrix())
    if pickle:
      write_pickle(csv_path + "/" + name + ".pickle", tables[name].matrix())
  pbar.set_description("Done")

def get_basename(filename):
  return splitext(basename(filename))[0]

def get_filename_ext(filename):
  return splitext(basename(filename))[1]

def filter_filenames_by_ext(filenames, ext):
  if ext is None:
    return filenames
  return [filename for filename in filenames if get_filename_ext(filename) == ext]

def get_full_filename(parent, relative):
  return parent + '/' + relative

def filter_filenames_by_files(parent, filenames):
  return [filename for filename in filenames if isfile(get_full_filename(parent, filename))]

def listfiles(root_dir):
  return filter_filenames_by_files(root_dir, listdir(root_dir))

def process_files_in_zip(zip_filename, process_file, ext=None):
  with ZipFile(zip_filename) as zip_archive:
    pbar = tqdm(filter_filenames_by_ext(zip_archive.namelist(), ext), leave=False)
    for filename in pbar:
      pbar.set_description(rjust_and_shorten_text(filename, width=40))
      with zip_archive.open(filename, 'r') as zip_file:
        try:
          # process_file(filename, zip_file.read())
          process_file(filename, zip_file)
        except xml.etree.ElementTree.ParseError as err:
          pbar.write("Parse error in file {}/{}: {}".format(
            zip_filename, filename, err))
    pbar.set_description("Done")

def sort_relative_filenames_by_file_modified_time(parent_dir, filenames):
  paired_with_timestamp = [
    (
      os.path.getmtime(os.path.join(parent_dir, filename)),
      filename
    )
    for filename in filenames
  ]
  sorted_pairs = sorted(paired_with_timestamp)
  unpaired_filenames = [
    pair[1] for pair in sorted_pairs
  ]
  return unpaired_filenames

def process_files_in_directory(root_dir, process_file, ext=None):
  filenames = listfiles(root_dir)
  if ext is not None:
    filenames =\
      filter_filenames_by_ext(filenames, ext) +\
      filter_filenames_by_ext(filenames, '.zip')
  sorted_filenames = sort_relative_filenames_by_file_modified_time(
    root_dir, set(filenames)
  )
  pbar = tqdm(sorted_filenames, leave=False)
  for filename in pbar:
    pbar.set_description(rjust_and_shorten_text(filename, width=40))
    full_filename = os.path.join(root_dir, filename)
    if get_filename_ext(filename) == '.zip' and ext != '.zip':
      process_files_in_zip(full_filename, process_file, ext)
    else:
      with open(full_filename, 'rb') as f:
        try:
          process_file(filename, f)
        except Exception as e:
          raise Exception('failed to process ' + full_filename) from e

def process_files_in_directory_or_zip(root_dir_or_zip, process_file, ext=None):
  if get_filename_ext(root_dir_or_zip) == '.zip':
    process_files_in_zip(root_dir_or_zip, process_file, ext)
  else:
    process_files_in_directory(root_dir_or_zip, process_file, ext)
