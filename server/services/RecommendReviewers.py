import pandas as pd

def column_astype(df, col_name, col_type):
  df = df.copy()
  df[col_name] = df[col_name].astype(col_type)
  return df

def applymap_dict_list(dict_list, f):
  return [dict((k, f(v)) for k, v in row.items()) for row in dict_list]

def nat_to_none(x):
  return None if type(x) == type(pd.NaT) else x

def clean_result(result):
  return applymap_dict_list(result, nat_to_none)

def droplevel_keep_non_blanks(columns):
  return [c[-1] if c[-1] != '' else c[0] for c in columns]

def groupby_agg_droplevel(df, groupby_columns, agg_param):
  # see https://github.com/pandas-dev/pandas/issues/8870
  df = df.groupby(groupby_columns, as_index=False).agg(agg_param)
  # magic droplevel that retains the main level if sub level label is blank
  df.columns = droplevel_keep_non_blanks(df.columns)
  return df

# def clean_df(df):
#   # TODO fix replace NaT
#   #return df.where((pd.notnull(df)), None)
#   return df.applymap(lambda x: None if type(x) == type(pd.NaT) else x)

class RecommendReviewers(object):
  def __init__(self, datasets):
    self.manuscript_keywords_df = datasets["manuscript-keywords"].drop('sequence', axis=1).copy()
    self.authors_df = datasets["authors"]
    self.persons_df = datasets["persons-current"].set_index('person-id')
    self.manuscript_history_df = datasets['manuscript-history']
    self.manuscript_keywords_df = self.manuscript_keywords_df.copy()
    self.manuscript_keywords_df['manuscript-no'] = self.manuscript_keywords_df['base-manuscript-number'].apply(
      lambda x: x.split('-')[-1]
    )

  def __find_manuscripts_by_keywords(self, keywords, version_key=None):
    other_manuscripts = self.manuscript_keywords_df[
      self.manuscript_keywords_df['word'].isin(keywords)
    ]
    other_manuscripts = other_manuscripts[other_manuscripts['version-key'] != version_key]
    other_manuscripts = groupby_agg_droplevel(
      other_manuscripts,
      ['base-manuscript-number', 'manuscript-number', 'version-key'],
      {
        'word': {
          'keywords': lambda x: tuple(x),
          'count': pd.np.size
        }
      }
    )
    return other_manuscripts

  def __find_authors_by_manuscripts(self, manuscripts):
    other_authors = self.authors_df[self.authors_df['base-manuscript-number'].isin(
      manuscripts['base-manuscript-number'])]
    other_authors = other_authors[['base-manuscript-number', 'author-person-id']].\
      drop_duplicates()
    other_authors = other_authors.rename(columns={
      'author-person-id': 'person-id'
    })
    return other_authors

  def __find_previous_reviewers_by_manuscripts(self, manuscripts):
    previous_reviewers = self.manuscript_history_df[
      self.manuscript_history_df['base-manuscript-number'].isin(
        manuscripts['base-manuscript-number'])]
    previous_reviewers = previous_reviewers[previous_reviewers['stage-name'] == 'Review Complete']
    previous_reviewers = previous_reviewers[
      ['base-manuscript-number', 'stage-affective-person-id']].drop_duplicates()
    previous_reviewers = previous_reviewers.rename(columns={
      'stage-affective-person-id': 'person-id'
    })
    return previous_reviewers

  def __find_manuscripts_by_key(self, manuscript_no):
    return self.manuscript_keywords_df[
      self.manuscript_keywords_df['manuscript-no'] == manuscript_no
    ]

  def __add_person_info(self, df, person_id_key='person-id'):
    return df.merge(
      right=self.persons_df.reset_index(),
      how='left',
      left_on=person_id_key,
      right_on='person-id')

  def __parse_keywords(self, keywords):
    if keywords.strip() == '':
      return []
    return [keyword.strip() for keyword in keywords.split(',')]

  def recommend(self, keywords, manuscript_no):
    keyword_list = self.__parse_keywords(keywords)
    if manuscript_no is not None and manuscript_no != '':
      matching_manuscripts = self.__find_manuscripts_by_key(manuscript_no)
      manuscript_keywords = matching_manuscripts['word']
      keyword_list += list(manuscript_keywords.values)
    else:
      matching_manuscripts = self.__find_manuscripts_by_key(None)
    print("keyword_list:", keyword_list)
    other_manuscripts = self.__find_manuscripts_by_keywords(
      keyword_list
    )
    # TODO add reviewers of papers as well as early career reviewers
    # TODO sort accordingly
    # TODO use topic modelling
    other_authors = self.__add_person_info(
      self.__find_authors_by_manuscripts(other_manuscripts)
    )
    previous_reviewers = self.__add_person_info(
      self.__find_previous_reviewers_by_manuscripts(other_manuscripts)
    )
    potential_reviewers_columns = [
      'person-id', 'base-manuscript-number',
      'title', 'first-name', 'middle-name', 'last-name', 'institution']
    potential_reviewers = pd.concat([
      other_authors[potential_reviewers_columns],
      previous_reviewers[potential_reviewers_columns]
    ])
    return {
      'potential-reviewers': clean_result(
        potential_reviewers\
        .to_dict(orient='records')),
      'matching-manuscripts': clean_result(
        matching_manuscripts\
        .reset_index()\
        [['base-manuscript-number', 'manuscript-number', 'version-key']]\
        .drop_duplicates()
        .to_dict(orient='records')
      )
    }
