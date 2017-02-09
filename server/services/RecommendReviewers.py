from itertools import groupby
import html

import pandas as pd

flatten = lambda l: [item for sublist in l for item in sublist]

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
      item for item in [
        vf(version_key) for version_key in
        set([version_key for _, version_key in list(v)])
      ] if item
    ]
    for k, v in groupby(zip(groupby_keys, version_keys), lambda x: x[0])
  }

def filter_dict_keys(d, f):
  return {k: v for k, v in d.items() if f(k)}

def groupby_column_to_dict(df, groupby_col):
  a = df.to_dict(orient='records')
  return {
    k: [filter_dict_keys(item, lambda col: col != groupby_col) for item in v]
    for k, v in groupby(a, lambda item: item[groupby_col])
  }

def groupby_index_to_dict(df):
  return groupby_column_to_dict(df, df.index.name)

def map_to_dict(keys, d, default_value=None):
  return [d.get(k, default_value) for k in keys]

# def clean_df(df):
#   # TODO fix replace NaT
#   #return df.where((pd.notnull(df)), None)
#   return df.applymap(lambda x: None if type(x) == type(pd.NaT) else x)

MANUSCRIPT_ID_COLUMNS = ['base-manuscript-number', 'manuscript-number', 'version-key']

PERSON_ID = 'person-id'
VERSION_KEY = 'version-key'

PERSON_COLUMNS = [
  'person-id',
  'title', 'first-name', 'middle-name', 'last-name', 'institution', 'status'
]

def filter_accepted_manuscript_versions(manuscript_versions):
  return manuscript_versions[
    manuscript_versions['decision'].isin(['Accept Full Submission', 'Auto-Accept'])
  ]

def filter_by(df, col_name, values):
  return df[df[col_name].isin(values)]

def unescape_if_string(s):
  if isinstance(s, str):
    return html.unescape(s)
  return s

def create_stage_pivot(stage_history):
  return stage_history.pivot_table(
    index=['manuscript-number', 'version-key', 'stage-affective-person-id'],
    columns='stage-name',
    values='start-date',
    aggfunc='first')

def duration_stats_between_by_person(stage_pivot, from_stage, to_stage):
  min_duration = pd.Timedelta(minutes=10)
  if (from_stage in stage_pivot.columns) and (to_stage in stage_pivot.columns):
    duration = stage_pivot[to_stage] - stage_pivot[from_stage]
    duration = duration[duration > min_duration]
  else:
    return pd.DataFrame([])
  duration = duration.astype('timedelta64[s]')
  return duration.dropna()\
  .to_frame('duration')\
  .reset_index()\
  .rename(columns={'stage-affective-person-id': 'person-id'})\
  .groupby('person-id', as_index=False)\
  .agg([
    pd.np.min, pd.np.mean, pd.np.max
  ])['duration'].rename(columns={
    'amin': 'min',
    'amax': 'max'
  })\
  / (24 * 60 * 60)

class RecommendReviewers(object):
  def __init__(self, datasets):
    self.manuscript_versions_df = filter_accepted_manuscript_versions(
      datasets['manuscript-versions'].copy().rename(columns={
        'key': 'version-key'
      })
    )
    self.manuscript_versions_df['title'] = self.manuscript_versions_df['title'].apply(
      lambda title: html.unescape(title)
    )
    self.manuscript_last_versions_df = self.manuscript_versions_df\
      .sort_values(VERSION_KEY)\
      .groupby(['base-manuscript-number', 'manuscript-number'], as_index=False)\
      .last()
    valid_version_keys = self.manuscript_last_versions_df[VERSION_KEY]
    self.manuscript_keywords_df = filter_by(
      datasets["manuscript-keywords"].drop('sequence', axis=1).copy(),
      VERSION_KEY,
      valid_version_keys
    )
    self.authors_df = filter_by(
      datasets["authors"],
      VERSION_KEY,
      valid_version_keys
    )
    self.manuscript_history_all_df = datasets['manuscript-history']
    self.manuscript_history_df = filter_by(
      self.manuscript_history_all_df,
      VERSION_KEY,
      valid_version_keys
    )

    self.persons_df = datasets["persons"].copy()
    memberships_df = datasets["person-memberships"].rename(columns={
      'person-key': PERSON_ID
    })
    dates_not_available_df = datasets["person-dates-not-available"].rename(columns={
      'person-key': PERSON_ID
    })
    dates_not_available_df = dates_not_available_df[
      dates_not_available_df['dna-end-date'] >= pd.to_datetime('today')
    ]

    self.manuscript_history_review_received_df = filter_by(
      self.manuscript_history_df,
      'stage-name',
      ['Review Received']
    )

    for c in PERSON_COLUMNS[1:]:
      self.persons_df[c] = self.persons_df[c].apply(unescape_if_string)

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

    temp_memberships_map = groupby_column_to_dict(memberships_df, PERSON_ID)
    dates_not_available_map = groupby_column_to_dict(dates_not_available_df, PERSON_ID)

    stage_pivot = create_stage_pivot(self.manuscript_history_all_df)
    review_durations_map = duration_stats_between_by_person(
      stage_pivot, 'Reviewers Accept', 'Review Received').to_dict(orient='index')

    persons_list = [{
      **person,
      'memberships': temp_memberships_map.get(person['person-id'], []),
      'dates-not-available': dates_not_available_map.get(person['person-id'], []),
      'stats': {
        'review-duration': review_durations_map.get(person['person-id'], None)
      }
    } for person in clean_result(self.persons_df[PERSON_COLUMNS].to_dict(orient='records'))]
    self.persons_map = dict((p[PERSON_ID], p) for p in persons_list)

    temp_authors_map = groupby_columns_to_dict(
      self.authors_df[VERSION_KEY].values,
      self.authors_df['author-person-id'].values,
      lambda person_id: self.persons_map.get(person_id, None)
    )

    temp_reviewers_map = groupby_columns_to_dict(
      self.manuscript_history_review_received_df[VERSION_KEY].values,
      self.manuscript_history_review_received_df['stage-affective-person-id'].values,
      lambda person_id: self.persons_map.get(person_id, None)
    )

    manuscripts_list = clean_result(
      self.manuscript_last_versions_df[MANUSCRIPT_ID_COLUMNS + ['title']]\
      .to_dict(orient='records'))
    manuscripts_list = [{
      **manuscript,
      'authors': temp_authors_map.get(manuscript[VERSION_KEY], []),
      'reviewers': temp_reviewers_map.get(manuscript[VERSION_KEY], [])
    } for manuscript in manuscripts_list]
    self.manuscripts_by_version_key_map = dict((m[VERSION_KEY], m) for m in manuscripts_list)

    self.manuscripts_by_author_map = {}
    self.manuscripts_by_reviewer_map = {}
    for m in manuscripts_list:
      for author in m['authors']:
        self.manuscripts_by_author_map.setdefault(author[PERSON_ID], [])\
        .append(m)
      for reviewer in m['reviewers']:
        self.manuscripts_by_reviewer_map.setdefault(reviewer[PERSON_ID], [])\
        .append(m)

    # manuscripts_by_columns = lambda groupby_keys, version_keys:\
    #   groupby_columns_to_dict(
    #     groupby_keys, version_keys,
    #     lambda version_key: self.manuscripts_by_version_key_map.get(version_key, None)
    #   )

    # self.manuscripts_by_author_map = manuscripts_by_columns(
    #   self.authors_df['author-person-id'].values,
    #   self.authors_df[VERSION_KEY].values
    # )

    # self.manuscripts_by_reviewer_map = manuscripts_by_columns(
    #   self.manuscript_history_review_received_df['stage-affective-person-id'].values,
    #   self.manuscript_history_review_received_df[VERSION_KEY].values
    # )

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
    other_authors = self.authors_df[self.authors_df[VERSION_KEY].isin(
      manuscripts[VERSION_KEY])]
    other_authors = other_authors[[VERSION_KEY, 'author-person-id']].\
      drop_duplicates()
    other_authors = other_authors.rename(columns={
      'author-person-id': 'person-id'
    })
    return other_authors

  def __find_previous_reviewers_by_manuscripts(self, manuscripts):
    previous_reviewers = self.manuscript_history_review_received_df[
      self.manuscript_history_review_received_df[VERSION_KEY].isin(
        manuscripts[VERSION_KEY])]
    previous_reviewers = previous_reviewers[
      [VERSION_KEY, 'stage-affective-person-id']].drop_duplicates()
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
    print("other_manuscripts:", other_manuscripts)
    # TODO add reviewers of papers as well as early career reviewers
    # TODO sort accordingly
    # TODO use topic modelling
    other_manuscripts_dicts = [
      self.manuscripts_by_version_key_map.get(version_key)
      for version_key in other_manuscripts[VERSION_KEY]
    ]
    other_manuscripts_dicts = [m for m in other_manuscripts_dicts if m]
    potential_reviewers_ids = set([
      person[PERSON_ID] for person in
      flatten([(m['authors'] + m['reviewers']) for m in other_manuscripts_dicts])
    ])
    # print("potential_reviewers_ids", potential_reviewers_ids)
    # for m in other_manuscripts_dicts:
    #   print("author_ids", m[VERSION_KEY], [p[PERSON_ID] for p in m['authors']])

    keyword_match_count_by_by_version_key_map = {
      k: v['count']
      for k, v in other_manuscripts[[VERSION_KEY, 'count']]\
      .set_index(VERSION_KEY).to_dict(orient='index').items()
    }
    # print("keyword_match_count_by_by_version_key_map:", keyword_match_count_by_by_version_key_map)

    def populate_potential_reviewer(person_id):
      author_of_manuscripts = self.manuscripts_by_author_map.get(person_id, [])
      reviewer_of_manuscripts = self.manuscripts_by_reviewer_map.get(person_id, [])
      involved_manuscripts = author_of_manuscripts + reviewer_of_manuscripts
      total_keyword_match_count = float(sum([
        keyword_match_count_by_by_version_key_map.get(manuscript[VERSION_KEY], 0)
        for manuscript in involved_manuscripts
      ]))
      if len(keyword_list) > 0:
        total_keyword_match_count = total_keyword_match_count / len(keyword_list)
      if total_keyword_match_count == 0:
        print("person_id:", person_id)
        print("author_of_manuscripts:", [m[VERSION_KEY] for m in author_of_manuscripts])
        print("reviewer_of_manuscripts:", [m[VERSION_KEY] for m in reviewer_of_manuscripts])
        print("involved_manuscripts:", [m[VERSION_KEY] for m in involved_manuscripts])
        print("total_keyword_match_count:", total_keyword_match_count)

      return {
        'person': self.persons_map.get(person_id, None),
        'author-of-manuscripts': author_of_manuscripts,
        'reviewer-of-manuscripts': reviewer_of_manuscripts,
        'scores': {
          'keyword': total_keyword_match_count
        }
      }

    potential_reviewers = [
      populate_potential_reviewer(person_id)
      for person_id in potential_reviewers_ids]

    available_potential_reviewer_mean_durations = [
      potential_reviewer['person']['stats']['review-duration']['mean']
      for potential_reviewer in potential_reviewers
      if potential_reviewer['person']['stats']['review-duration']
    ]
    potential_reviewer_mean_duration = float(pd.np.mean(
      available_potential_reviewer_mean_durations))

    potential_reviewers = sorted(
      potential_reviewers,
      key=lambda potential_reviewer: (
        -potential_reviewer['scores']['keyword'],
        (
          potential_reviewer['person']['stats']['review-duration']['mean']
          if potential_reviewer['person']['stats']['review-duration']
          else potential_reviewer_mean_duration
        ),
        potential_reviewer['person']['first-name'],
        potential_reviewer['person']['last-name']
      )
    )

    return {
      'potential-reviewers': potential_reviewers,
      'matching-manuscripts': map_to_dict(
        matching_manuscripts[VERSION_KEY],
        self.manuscripts_by_version_key_map
      )
    }
