from os import makedirs
from os.path import isfile
from textwrap import shorten

import boto3
from tqdm import tqdm

# Prerequisites:
# * Credentials setup in user profile

bucket_name = "elife-ejp-ftp-db-xml-dump"

s3 = boto3.resource('s3')

client = boto3.client('s3')

bucket = s3.Bucket(bucket_name)

download_path = "../downloads"

makedirs(download_path, exist_ok=True)

pbar = tqdm(list(bucket.objects.all()), leave=False)
for obj in pbar:
  remote_file = obj.key
  pbar.set_description("%40s" % shorten(remote_file, width=40))
  local_file = download_path + '/' + remote_file
  if not isfile(local_file):
    client.download_file(bucket_name, remote_file, local_file)

print("Done")
