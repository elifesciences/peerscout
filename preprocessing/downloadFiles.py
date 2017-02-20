from os import makedirs
from os.path import isfile
from textwrap import shorten

import boto3
from tqdm import tqdm

# Prerequisites:
# * Credentials setup in user profile

def download_objects(client, obj_list, download_path):
  makedirs(download_path, exist_ok=True)

  pbar = tqdm(list(obj_list), leave=False)
  for obj in pbar:
    remote_file = obj.key
    pbar.set_description("%40s" % shorten(remote_file, width=40))
    local_file = download_path + '/' + remote_file
    if not isfile(local_file):
      client.download_file(obj.bucket_name, remote_file, local_file)


def main():
  s3 = boto3.resource('s3')

  client = boto3.client('s3')

  download_objects(
    client,
    s3.Bucket("elife-ejp-ftp-db-xml-dump").objects.all(),
    "../downloads")

  download_objects(
    client,
    s3.Bucket("elife-ejp-ftp").objects.filter(
      Prefix="ejp_query_tool_query_id_380_DataScience:_Early_Career_Researchers"
    ),
    "../downloads-ftp")

  print("Done")

if __name__ == "__main__":
  main()
