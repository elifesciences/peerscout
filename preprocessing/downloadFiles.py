from os import makedirs
from os.path import isfile
from textwrap import shorten
import logging

import boto3
from tqdm import tqdm

from preprocessingUtils import get_downloads_csv_path, get_downloads_xml_path

from shared_proxy.app_config import get_app_config

NAME = 'downloadFiles'

# Prerequisites:
# * Credentials setup in user profile

def download_objects(client, obj_list, download_path, downloaded_files=None):
  makedirs(download_path, exist_ok=True)

  pbar = tqdm(list(obj_list), leave=False)
  for obj in pbar:
    remote_file = obj.key
    pbar.set_description("%40s" % shorten(remote_file, width=40))
    local_file = download_path + '/' + remote_file
    if not isfile(local_file):
      client.download_file(obj.bucket_name, remote_file, local_file)
      if downloaded_files is not None:
        downloaded_files.append(remote_file)

def configure_boto_logging():
  logging.getLogger('boto3').setLevel(logging.WARNING)
  logging.getLogger('botocore').setLevel(logging.WARNING)
  logging.getLogger('nose').setLevel(logging.WARNING)

def s3_object_list(s3, bucket, prefix=None):
  if not bucket:
    return []
  if prefix:
    return s3.Bucket(bucket).objects.filter(Prefix=prefix)
  else:
    return s3.Bucket(bucket).objects.all()

def main():
  app_config = get_app_config()
  storage_config = dict(app_config['storage']) if 'storage' in app_config else {}

  configure_boto_logging()

  s3 = boto3.resource('s3')

  client = boto3.client('s3')

  downloaded_files = []

  download_objects(
    client,
    s3_object_list(s3, storage_config.get('xml_dump_bucket')),
    get_downloads_xml_path(),
    downloaded_files)

  download_objects(
    client,
    s3_object_list(s3, storage_config.get('ecr_bucket'), storage_config.get('ecr_prefix')),
    get_downloads_csv_path(),
    downloaded_files)

  download_objects(
    client,
    s3_object_list(s3, storage_config.get('editors_bucket'), storage_config.get('editors_prefix')),
    get_downloads_csv_path(),
    downloaded_files)

  logger = logging.getLogger(NAME)
  logger.info('%d files downloaded', len(downloaded_files))
  logger.info('done')

  return len(downloaded_files) > 0

if __name__ == "__main__":
  from shared_proxy import configure_logging
  configure_logging('update')

  main()
