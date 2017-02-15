import pandas as pd

def read_csv(*args, **kwargs):
  # df_headers = pd.read_csv(*args, nrows=1, encoding='utf-8')
  df_headers = pd.read_csv(*args, **kwargs, nrows=1, encoding='utf-8')
  parse_dates = []
  for column in df_headers.columns:
    if column.endswith('-date'):
      parse_dates.append(column)
  return pd.read_csv(*args, encoding='utf-8', parse_dates=parse_dates, low_memory=False)
  # return pd.read_csv(*args, **kwargs, encoding='utf-8', parse_dates=parse_dates, low_memory=False)

class CsvDatasetLoader(object):
  def __init__(self, csv_path):
    self.csv_path = csv_path

  def get_csv(self, filename, *args, **kwargs):
    df = read_csv(self.csv_path + "/" + filename, *args, **kwargs)
    print("df {} shape {}".format(filename, df.shape))
    return df

  def __getitem__(self, key):
    return self.get_csv(key + '.csv')
