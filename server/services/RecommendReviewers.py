from itertools import groupby
import html

import pandas as pd

def column_astype(df, col_name, col_type):
  df = df.copy()
  df[col_name] = df[col_name].astype(col_type)
  return df

def applymap_dict_list(dict_list, f):
  return [dict((k, f(v)) for k, v in row.items()) for row in dict_list]

def is_nat(x):
  return isinstance(x, type(pd.NaT))

def is_null(x):
  return pd.isnull(x) or is_nat(x)

def nat_to_none(x):
  return None if is_nat(x) else x

def remove_none(d):
  return dict((k, v) for k, v in d.items() if not is_null(v))

def clean_result(result):
  return [remove_none(x) for x in applymap_dict_list(result, nat_to_none)]

def droplevel_keep_non_blanks(columns):
  return [c[-1] if c[-1] != '' else c[0] for c in columns]

def groupby_agg_droplevel(df, groupby_columns, agg_param):
  # see https://github.com/pandas-dev/pandas/issues/8870
  df = df.groupby(groupby_columns, as_index=False).agg(agg_param)
  # magic droplevel that retains the main level if sub level label is blank
  df.columns = droplevel_keep_non_blanks(df.columns)
  return df

def manuscript_number_to_no(x):
  return x.split('-')[-1]

def groupby_to_dict(l, kf, vf):
  return {
    k: vf(l(v))
    for k, v in groupby(l, kf)
  }

def groupby_columns_to_dict(groupby_keys, version_keys, vf):
  return {
    k: [
      vf(version_key)
      for _, version_key in set(v)
      if vf(version_key)
    ]
    for k, v in groupby(zip(groupby_keys, version_keys), lambda x: x[0])
  }

def map_to_dict(keys, d, default_value=None):
  return [d.get(k, default_value) for k in keys]

# def clean_df(df):
#   # TODO fix replace NaT
#   #return df.where((pd.notnull(df)), None)
#   return df.applymap(lambda x: None if type(x) == type(pd.NaT) else x)

MANUSCRIPT_ID_COLUMNS = ['base-manuscript-number', 'manuscript-number', 'version-key']

PERSON_ID = 'person-id'
VERSION_KEY = 'version-key'

PERSON_COLUMNS = ['person-id', 'title', 'first-name', 'middle-name', 'last-name', 'institution']

def filter_accepted_manuscript_versions(manuscript_versions):
  return manuscript_versions[
    manuscript_versions['decision'].isin(['Accept Full Submission', 'Auto-Accept'])
  ]

def unescape_if_string(s):
  if isinstance(s, str):
    return html.unescape(s)
  return s

class RecommendReviewers(object):
  def __init__(self, datasets):
    self.manuscript_keywords_df = datasets["manuscript-keywords"].drop('sequence', axis=1).copy()
    self.authors_df = datasets["authors"]
    self.persons_df = datasets["persons-current"].copy()
    self.manuscript_history_df = datasets['manuscript-history']

    for c in PERSON_COLUMNS[1:]:
      self.persons_df[c] = self.persons_df[c].apply(unescape_if_string)

    self.manuscript_versions_df = filter_accepted_manuscript_versions(
      datasets['manuscript-versions'].copy().rename(columns={
        'key': 'version-key'
      })
    )
    self.manuscript_versions_df['title'] = self.manuscript_versions_df['title'].apply(
      lambda title: html.unescape(title)
    )
    self.manuscript_versions_df['manuscript-no'] =\
      self.manuscript_versions_df['base-manuscript-number'].apply(
        manuscript_number_to_no
      )

    self.manuscript_keywords_df = self.manuscript_keywords_df.copy()
    self.manuscript_keywords_df = self.manuscript_keywords_df[
      self.manuscript_keywords_df[VERSION_KEY].isin(
        self.manuscript_versions_df[VERSION_KEY]
      )
    ][MANUSCRIPT_ID_COLUMNS + ['word']].drop_duplicates()
    persons_list = clean_result(self.persons_df[PERSON_COLUMNS].to_dict(orient='records'))
    self.persons_map = dict((p[PERSON_ID], p) for p in persons_list)

    temp_authors_map = groupby_columns_to_dict(
      self.authors_df[VERSION_KEY].values,
      self.authors_df['author-person-id'].values,
      lambda person_id: self.persons_map.get(person_id, None)
    )

    temp_reviewers_map = groupby_columns_to_dict(
      self.manuscript_history_df[VERSION_KEY].values,
      self.manuscript_history_df['stage-affective-person-id'].values,
      lambda person_id: self.persons_map.get(person_id, None)
    )

    manuscripts_list = clean_result(
      self.manuscript_versions_df[MANUSCRIPT_ID_COLUMNS + ['title']]\
      .drop_duplicates().to_dict(orient='records'))
    manuscripts_list = [{
      **manuscript,
      'authors': temp_authors_map.get(manuscript[VERSION_KEY], []),
      'reviewers': temp_reviewers_map.get(manuscript[VERSION_KEY], [])
    } for manuscript in manuscripts_list]
    self.manuscripts_by_version_key_map = dict((m[VERSION_KEY], m) for m in manuscripts_list)
    print("self.manuscripts_by_version_key_map:", self.manuscripts_by_version_key_map)

    manuscripts_by_columns = lambda groupby_keys, version_keys:\
      groupby_columns_to_dict(
        groupby_keys, version_keys,
        lambda version_key: self.manuscripts_by_version_key_map.get(version_key, None)
      )

    self.manuscripts_by_author_map = manuscripts_by_columns(
      self.authors_df['author-person-id'].values,
      self.authors_df[VERSION_KEY].values
    )

    self.manuscripts_by_reviewer_map = manuscripts_by_columns(
      self.manuscript_history_df['stage-affective-person-id'].values,
      self.manuscript_history_df[VERSION_KEY].values
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

  def __find_keywords_by_version_keys(self, version_keys):
    return self.manuscript_keywords_df[
      self.manuscript_keywords_df[VERSION_KEY].isin(version_keys)
    ]['word']

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
    return self.manuscript_versions_df[
      self.manuscript_versions_df['manuscript-no'] == manuscript_no
    ].sort_values('version-key').groupby('manuscript-no').last()

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
      manuscript_keywords = self.__find_keywords_by_version_keys(matching_manuscripts[VERSION_KEY])
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
    other_authors = self.__find_authors_by_manuscripts(other_manuscripts)
    previous_reviewers = self.__find_previous_reviewers_by_manuscripts(other_manuscripts)
    potential_reviewers_ids = pd.concat([
      other_authors[['person-id']],
      previous_reviewers[['person-id']]
    ]).drop_duplicates()[PERSON_ID]
    potential_reviewers = [{
      'person': self.persons_map.get(person_id, None),
      'author-of-manuscripts': self.manuscripts_by_author_map.get(person_id, []),
      'reviewer-of-manuscripts': self.manuscripts_by_reviewer_map.get(person_id, [])
    } for person_id in potential_reviewers_ids]

    return {
      'potential-reviewers': potential_reviewers,
      'matching-manuscripts': map_to_dict(
        matching_manuscripts[VERSION_KEY],
        self.manuscripts_by_version_key_map
      )
    }
