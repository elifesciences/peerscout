from os import listdir
import os

import pandas as pd

from convertUtils import filter_filenames_by_ext

def convert_xml_file_to(filename, stream, csv_path):
  print("converting:", filename)
  df = pd.read_csv(stream, skiprows=3)
  print("shape:", df.shape)
  # keep columns consistent with persons
  df = df.rename(columns={
    'p_id': 'person-id',
    'first_nm': 'first-name',
    'last_nm': 'last-name'
  })
  print("columns:", df.columns.values)
  out_filename = os.path.join(csv_path, 'early-career-reviewers.csv')
  print("writing result to:", out_filename)
  df.to_csv(out_filename, index=False)
  df.to_pickle(os.path.join(csv_path, 'early-career-reviewers.pickle'))

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
  source = '../../downloads-ftp'
  csv_path = "../../csv"

  process_file = lambda filename, stream:\
    convert_xml_file_to(filename, stream, csv_path)

  convert_last_csv_files_in_directory(
    source,
    process_file,
    prefix="ejp_query_tool_query_id_380_DataScience:_Early_Career_Researchers"
  )

  print("Done")

if __name__ == "__main__":
  main()
