from os import listdir
import os
import logging

import pandas as pd

from .convertUtils import (
  filter_filenames_by_ext
)

from .preprocessingUtils import get_downloads_csv_path

from ..shared.app_config import get_app_config

NAME = 'convertEditorsCsv'

def get_logger():
  return logging.getLogger(NAME)

def read_editors_csv_as_data_frame(stream):
  return pd.read_csv(stream, skiprows=3)

def extract_distinct_emails_from_data_frame(df):
  emails = set(df['email'])
  if 'secondary_email' in df.columns:
    emails |= set(df['secondary_email'])
  emails = {s.strip() for s in emails if s and not pd.isnull(s)}
  return emails - {''}

def convert_csv_file_to(filename, stream, valid_emails_filename):
  logger = get_logger()
  logger.info("converting: %s", filename)
  emails = sorted(extract_distinct_emails_from_data_frame(
    read_editors_csv_as_data_frame(stream)
  ))
  logger.info("emails: %d", len(emails))
  logger.info("writing to: %s", valid_emails_filename)
  os.makedirs(os.path.dirname(valid_emails_filename), exist_ok=True)
  with open(valid_emails_filename, 'w') as f:
    f.write('\n'.join(emails))

def convert_last_csv_files_in_directory(root_dir, process_file, prefix):
  files = sorted([
    fn
    for fn in filter_filenames_by_ext(listdir(root_dir), '.csv')
    if fn.startswith(prefix)
  ])
  filename = files[-1]
  if filename is not None:
    with open(os.path.join(root_dir, filename), 'rb') as f:
      process_file(filename, f)
  else:
    raise Exception("no csv files found with prefix {} in directory {}".format(prefix, root_dir))

def main():
  app_config = get_app_config()
  editors_prefix = app_config.get('storage', 'editors_prefix')
  if not editors_prefix:
    get_logger().info('editors_prefix not configured')

  valid_emails_filename = app_config.get('auth', 'valid_emails')
  if not valid_emails_filename:
    get_logger().info('valid_emails not configured')

  source = get_downloads_csv_path()

  process_file = lambda filename, stream:\
    convert_csv_file_to(filename, stream, valid_emails_filename)

  convert_last_csv_files_in_directory(
    source,
    process_file,
    prefix=editors_prefix
  )

  get_logger().info("Done")

if __name__ == "__main__":
  from ..shared.logging_config import configure_logging
  configure_logging('update')

  main()
