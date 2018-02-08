import pandas as pd

def droplevel_keep_non_blanks(columns):
  return [
    (c[-1] if c[-1] != '' else c[0])
    if isinstance(c, (tuple, list))
    else c
    for c in columns
  ]

class GroupAggregator(object):
  def __init__(self, groupby_columns, agg_param):
    self.groupby_columns = groupby_columns
    self.agg_columns_and_fn = sorted([
      (column, agg_name, agg_fn)
      for column, column_agg_param in agg_param.items()
      for agg_name, agg_fn in column_agg_param.items()
    ])
    self.result_columns = (
      groupby_columns +
      [(column, agg_name) for column, agg_name, _ in self.agg_columns_and_fn]
    )

  def add_empty_dataframe_columns(self, df):
    if len(df) == 0:
      df = pd.DataFrame([], columns=self.result_columns)
    return df

  def __call__(self, df):
    result_data = (
      [df[column].values[0] for column in self.groupby_columns] +
      [agg_fn(df[column]) for column, _, agg_fn in self.agg_columns_and_fn]
    )
    return pd.Series(result_data, index=self.result_columns)

def groupby_agg_droplevel(df, groupby_columns, agg_param):
  # warnings.warn('groupby_agg_droplevel: %s' % agg_param)
  # see https://github.com/pandas-dev/pandas/issues/8870
  if isinstance(agg_param, dict) and any(isinstance(x, dict) for x in agg_param.values()):
    aggregator = GroupAggregator(groupby_columns, agg_param)
    df = aggregator.add_empty_dataframe_columns(df.groupby(
      groupby_columns, as_index=False
    ).apply(aggregator))
  else:
    df = df.groupby(groupby_columns, as_index=False).agg(agg_param)
  # magic droplevel that retains the main level if sub level label is blank
  df.columns = droplevel_keep_non_blanks(df.columns)
  return df
