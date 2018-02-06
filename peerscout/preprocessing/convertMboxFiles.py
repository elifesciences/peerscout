import csv
from os import SEEK_END

from tqdm import tqdm

from .mbox_parser import split_messages_skip_content, parse_header_properties

from .convertUtils import process_files_in_directory_or_zip

from .preprocessingUtils import get_data_path, get_db_path

def stream_size(stream):
  if stream.seekable():
    cur_position = stream.tell()
    stream.seek(0, SEEK_END)
    file_size = stream.tell()
    stream.seek(cur_position)
    return file_size
  else:
    return None

def stream_position(stream):
  if stream.seekable():
    return stream.tell()
  else:
    return None


def convert_mbox_file(filename, stream, writer, fieldnames):
  file_size = stream_size(stream)
  prev_pos = 0
  pos_unit = 1024 * 1024
  with tqdm(total=file_size // pos_unit if file_size is not None else None) as pbar:
    pbar.set_description(filename)
    for lines in split_messages_skip_content(stream):
      cur_pos = stream_position(stream)
      if cur_pos is not None:
        pos_change = (cur_pos - prev_pos) // pos_unit
        if pos_change > 0:
          pbar.update(pos_change)
        prev_pos = cur_pos
      else:
        pbar.update()

      header_dict = dict(
        (k, v)
        for k, v in parse_header_properties(lines, required_keys=fieldnames)
      )
      writer.writerow(header_dict)

def main():

  csv_path = get_db_path()
  source = get_data_path('emails-mbox')

  with open(csv_path + '/email-mbox-meta.csv', 'w') as csvfile:
    fieldnames = [
      'Date', 'Received', 'From', 'Return-Path', 'Subject', 'To',
      'Delivered-To', 'Message-ID', 'In-Reply-To', 'References',
      'X-GM-THRID', 'X-Gmail-Labels'
    ]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')

    writer.writeheader()

    process_file = lambda filename, stream:\
      convert_mbox_file(filename, stream, writer, fieldnames)

    process_files_in_directory_or_zip(source, process_file, ext='.mbox')

  print("done")

if __name__ == "__main__":
  main()
