from itertools import groupby
import itertools
import ast
from datetime import datetime

import pandas as pd

from .ManuscriptModel import is_manuscript_relevant

from .utils import unescape_and_strip_tags, filter_by

from .collection_utils import flatten, filter_none, deep_get, deep_get_list

debug_enabled = False

def set_debug_enabled(enabled):
  global debug_enabled
  debug_enabled = enabled

def debug(*args):
  if debug_enabled:
    print(*args)

to_int = lambda x, default_value=None: int(x) if x is not None else default_value

def get_first(l, default_value=None):
  return l[0] if l else default_value

def column_astype(df, col_name, col_type):
  df = df.copy()
  df[col_name] = df[col_name].astype(col_type)
  return df

def applymap_dict(d, f):
  return dict((k, f(v)) for k, v in d.items())

def applymap_dict_list(dict_list, f):
  return [applymap_dict(row, f) for row in dict_list]

def is_nat(x):
  return isinstance(x, type(pd.NaT))

def is_null(x):
  return pd.isnull(x) or is_nat(x)

def nat_to_none(x):
  return None if is_nat(x) else x

def null_to_none(x):
  return None if is_null(x) else x

def remove_none(d):
  return dict((k, v) for k, v in d.items() if not is_null(v))

def clean_result(result):
  if isinstance(result, list):
    return [clean_result(x) for x in result]
  else:
    return remove_none(applymap_dict(result, nat_to_none))

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
    k: [vf(v) for v in g]
    for k, g in groupby(sorted(l, key=kf), kf)
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

def groupby_column_to_dict(df, groupby_col, value_col=None):
  if value_col is None:
    value_f = lambda item: filter_dict_keys(item, lambda col: col != groupby_col)
  elif callable(value_col):
    value_f = value_col
  else:
    value_f = lambda item: item[value_col]
  a = df.to_dict(orient='records')
  return {
    k: [value_f(item) for item in v]
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

MANUSCRIPT_NO = 'manuscript-no'
VERSION_NO = 'version-no'
# internal composite id
MANUSCRIPT_VERSION_ID = 'manuscript-version-id'

RAW_MANUSCRIPT_ID_COLUMNS = [MANUSCRIPT_NO, VERSION_NO]
TEMP_MANUSCRIPT_ID_COLUMNS = [MANUSCRIPT_VERSION_ID]
MANUSCRIPT_ID_COLUMNS = RAW_MANUSCRIPT_ID_COLUMNS + TEMP_MANUSCRIPT_ID_COLUMNS

SIMILARITY_COLUMN = 'similarity'

PERSON_ID = 'person-id'

PERSON_COLUMNS = [
  'person-id',
  'title', 'first-name', 'middle-name', 'last-name', 'institution', 'status', 'email'
]

def unescape_if_string(s):
  if isinstance(s, str):
    return unescape_and_strip_tags(s)
  return s

def create_stage_pivot(stage_history):
  return stage_history.pivot_table(
    index=[MANUSCRIPT_NO, VERSION_NO, 'stage-affective-person-id'],
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
  SECONDS_PER_DAY = 24 * 60 * 60
  df = duration.dropna()\
  .to_frame('duration')\
  .reset_index()\
  .rename(columns={'stage-affective-person-id': 'person-id'})\
  .groupby('person-id', as_index=False)\
  .agg([
    pd.np.min, pd.np.mean, pd.np.max, pd.np.size
  ])['duration'].rename(columns={
    'amin': 'min',
    'amax': 'max',
    'size': 'count'
  })
  for c in ['min', 'max', 'mean']:
    df[c] = df[c] / SECONDS_PER_DAY
  return df

def filter_stage_pivot_by_stage(stage_pivot, stage, condition):
  if condition is not None and stage in stage_pivot.columns:
    return stage_pivot[
      stage_pivot[stage].apply(lambda dt: not is_null(dt) and condition(dt))
    ]
  else:
    return stage_pivot

def get_stage(stage_pivot, stage_name):
  return (
    stage_pivot[stage_name]
    if stage_name in stage_pivot.columns
    else [pd.NaT] * len(stage_pivot)
  )

def stats_by_person_for_period(stage_pivot, condition=None):
  review_duration_by_person_map = duration_stats_between_by_person(
    filter_stage_pivot_by_stage(stage_pivot, 'Review Received', condition),
    'Reviewers Accept', 'Review Received'
  ).to_dict(orient='index')
  reviews_in_progress_map = stage_pivot[
    pd.notnull(get_stage(stage_pivot, 'Reviewers Accept')) &
    pd.isnull(get_stage(stage_pivot, 'Review Received'))
  ].reset_index().groupby('stage-affective-person-id').size().to_dict()
  waiting_to_be_accepted_map = stage_pivot[
    pd.notnull(get_stage(stage_pivot, 'Contacting Reviewers')) &
    (
      pd.isnull(get_stage(stage_pivot, 'Reviewers Accept')) &
      pd.isnull(get_stage(stage_pivot, 'Reviewers Decline'))
    )
  ].reset_index().groupby('stage-affective-person-id').size().to_dict()
  declined_map = stage_pivot[
    pd.notnull(get_stage(stage_pivot, 'Reviewers Decline'))
  ].reset_index().groupby('stage-affective-person-id').size().to_dict()
  return clean_result(dict((k, {
    'review-duration': review_duration_by_person_map.get(k),
    'reviews-in-progress': int(reviews_in_progress_map.get(k, 0)),
    'waiting-to-be-accepted': int(waiting_to_be_accepted_map.get(k, 0)),
    'declined': int(declined_map.get(k, 0))
  }) for k in (
    set(review_duration_by_person_map.keys()) |
    set(reviews_in_progress_map.keys()) |
    set(waiting_to_be_accepted_map.keys()) |
    set(declined_map.keys())
  )))


def add_manuscript_version_id(df):
  df[MANUSCRIPT_VERSION_ID] = df[MANUSCRIPT_NO].str.cat(
    df[VERSION_NO].map(str), sep='-')
  return df

def select_dict_keys(d, keys):
  return {k: d[k] for k in keys}

def manuscript_id_fields(manuscript):
  return select_dict_keys(manuscript, MANUSCRIPT_ID_COLUMNS)

def person_by_early_career_reviewer(early_career_reviewer):
  memberships = []
  if len(early_career_reviewer['ORCID']) > 0:
    memberships.append({
      'member-type': 'ORCID',
      'member-id': early_career_reviewer['ORCID']
    })
  return {
    PERSON_ID: early_career_reviewer[PERSON_ID],
    'status': 'Active',
    'first-name': early_career_reviewer['first-name'],
    'last-name': early_career_reviewer['last-name'],
    'is-early-career-researcher': True,
    'memberships': memberships,
    'dates-not-available': [],
    'stats': {
    }
  }

def sort_manuscripts_by_date(manuscripts):
  return sorted(manuscripts, key=lambda m: (
    m.get('published-date', None),
    m.get('title', None),
    m.get(MANUSCRIPT_VERSION_ID, None)
  ), reverse=True)

def parse_list_if_str(x):
  if isinstance(x, str):
    return ast.literal_eval(x)
  return x

def manuscript_by_crossref_person_extra(crossref_person_extra):
  doi = crossref_person_extra['doi']
  return {
    MANUSCRIPT_VERSION_ID: doi,
    MANUSCRIPT_NO: doi,
    VERSION_NO: None,
    'doi': doi,
    'title': crossref_person_extra['title'],
    'abstract': crossref_person_extra['abstract'],
    'subject-areas': parse_list_if_str(crossref_person_extra['subject-areas']),
    'published-date': crossref_person_extra['created-date'],
    'authors': [],
    'reviewers': []
  }

class RecommendReviewers(object):
  def __init__(self, datasets, manuscript_model, similarity_model=None):
    self.similarity_model = similarity_model

    self.manuscript_versions_all_df = add_manuscript_version_id(
      datasets['manuscript-versions'].copy())
    for c in ['title', 'abstract']:
      self.manuscript_versions_all_df[c] = self.manuscript_versions_all_df[c].apply(
        unescape_if_string
      )
    valid_version_ids = manuscript_model.get_valid_manuscript_version_ids()
    self.manuscript_versions_df = filter_by(
      self.manuscript_versions_all_df,
      MANUSCRIPT_VERSION_ID,
      valid_version_ids
    )
    self.manuscript_keywords_all_df = add_manuscript_version_id(
      datasets["manuscript-keywords"]\
      .drop('sequence', axis=1).copy())
    self.manuscript_keywords_df = filter_by(
      self.manuscript_keywords_all_df,
      MANUSCRIPT_VERSION_ID,
      valid_version_ids
    )
    self.authors_all_df = add_manuscript_version_id(datasets["authors"])
    self.authors_df = filter_by(
      self.authors_all_df,
      MANUSCRIPT_VERSION_ID,
      valid_version_ids
    )
    self.editors_all_df = add_manuscript_version_id(datasets["editors"])
    self.senior_editors_all_df = add_manuscript_version_id(datasets["senior-editors"])
    self.manuscript_history_all_df = add_manuscript_version_id(
      datasets['manuscript-history'])
    self.manuscript_history_df = filter_by(
      self.manuscript_history_all_df,
      MANUSCRIPT_VERSION_ID,
      valid_version_ids
    )

    self.manuscript_subject_areas_all_df = add_manuscript_version_id(
      datasets['manuscript-themes']
      .rename(columns={'theme': 'subject-area'})
    )
    self.manuscript_subject_areas_df = filter_by(
      self.manuscript_subject_areas_all_df,
      MANUSCRIPT_VERSION_ID,
      valid_version_ids
    )

    manuscripts_df = datasets["manuscripts"]

    self.persons_df = datasets["persons"].copy()
    early_career_researchers_df = datasets["early-career-researchers"]
    self.early_career_researchers_df = early_career_researchers_df
    crossref_person_extras_df = datasets["crossref-person-extra"]

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

    self.assigned_reviewers_df = add_manuscript_version_id(
      datasets["potential-referees"]
    )

    for c in PERSON_COLUMNS[1:]:
      self.persons_df[c] = self.persons_df[c].apply(unescape_if_string)

    self.manuscript_keywords_df = self.manuscript_keywords_df.copy()
    self.manuscript_keywords_df = self.manuscript_keywords_df[
      self.manuscript_keywords_df[MANUSCRIPT_VERSION_ID].isin(
        self.manuscript_versions_df[MANUSCRIPT_VERSION_ID]
      )
    ][MANUSCRIPT_ID_COLUMNS + ['word']].drop_duplicates()

    temp_memberships_map = groupby_column_to_dict(memberships_df, PERSON_ID)
    dates_not_available_map = groupby_column_to_dict(dates_not_available_df, PERSON_ID)
    early_career_researchers_person_ids = set(early_career_researchers_df[PERSON_ID].values)

    print("gathering stats")
    stage_pivot = create_stage_pivot(self.manuscript_history_all_df)
    overall_stats_map = stats_by_person_for_period(stage_pivot)

    today = datetime.today()
    from_12m = pd.Timestamp(today.replace(year=today.year - 1))
    last12m_stats_map = stats_by_person_for_period(stage_pivot, lambda dt: dt >= from_12m)

    print("building person list")
    persons_list = [{
      **person,
      'is-early-career-researcher': person['person-id'] in early_career_researchers_person_ids,
      'memberships': temp_memberships_map.get(person['person-id'], []),
      'dates-not-available': dates_not_available_map.get(person['person-id'], []),
      'stats': {
        'overall': overall_stats_map.get(person['person-id'], None),
        'last-12m': last12m_stats_map.get(person['person-id'], None)
      }
    } for person in clean_result(self.persons_df[PERSON_COLUMNS].to_dict(orient='records'))]

    self.persons_map = dict((p[PERSON_ID], p) for p in persons_list)

    for row in early_career_researchers_df.to_dict(orient='records'):
      person_id = row[PERSON_ID]
      if person_id not in self.persons_map:
        self.persons_map[person_id] = person_by_early_career_reviewer(row)

    debug("self.persons_df:", self.persons_df)
    debug("persons_map:", self.persons_map)

    temp_authors_map = groupby_columns_to_dict(
      self.authors_all_df[MANUSCRIPT_VERSION_ID].values,
      self.authors_all_df['author-person-id'].values,
      lambda person_id: self.persons_map.get(person_id, None)
    )

    temp_editors_map = groupby_columns_to_dict(
      self.editors_all_df[MANUSCRIPT_VERSION_ID].values,
      self.editors_all_df['editor-person-id'].values,
      lambda person_id: self.persons_map.get(person_id, None)
    )

    temp_senior_editors_map = groupby_columns_to_dict(
      self.senior_editors_all_df[MANUSCRIPT_VERSION_ID].values,
      self.senior_editors_all_df['senior-editor-person-id'].values,
      lambda person_id: self.persons_map.get(person_id, None)
    )

    temp_reviewers_map = groupby_columns_to_dict(
      self.manuscript_history_review_received_df[MANUSCRIPT_VERSION_ID].values,
      self.manuscript_history_review_received_df['stage-affective-person-id'].values,
      lambda person_id: self.persons_map.get(person_id, None)
    )

    self.assigned_reviewers_by_manuscript_id_map = groupby_column_to_dict(
      self.assigned_reviewers_df,
      MANUSCRIPT_VERSION_ID,
      lambda row: dict({
        'person-id': row['potential-referee-person-id'],
        'status': row['potential-referee-status'],
        'excluded': row['potential-referee-suggested-to-exclude'] == 'yes'
      })
    )

    debug("self.manuscript_history_review_received_df:", self.manuscript_history_review_received_df)
    debug("temp_authors_map:", temp_authors_map)
    debug("temp_reviewers_map:", temp_reviewers_map)

    temp_doi_by_manuscript_no_map = groupby_column_to_dict(
      manuscripts_df,
      MANUSCRIPT_NO,
      'production-data-doi')

    self.all_subject_areas = set(self.manuscript_subject_areas_all_df['subject-area'])
    temp_subject_areas_map = groupby_column_to_dict(
      self.manuscript_subject_areas_all_df,
      MANUSCRIPT_VERSION_ID,
      'subject-area'
    )

    print("building manuscript list")
    manuscripts_all_list = clean_result(
      self.manuscript_versions_all_df[
        MANUSCRIPT_ID_COLUMNS +\
        ['title', 'decision', 'manuscript-type', 'abstract', 'decision-date']
      ].rename(columns={'decision-date': 'published-date'})
      .to_dict(orient='records'))
    manuscripts_all_list = [{
      **manuscript,
      'doi': get_first(temp_doi_by_manuscript_no_map.get(manuscript[MANUSCRIPT_NO], [])),
      'authors': temp_authors_map.get(manuscript[MANUSCRIPT_VERSION_ID], []),
      'editors': temp_editors_map.get(manuscript[MANUSCRIPT_VERSION_ID], []),
      'senior-editors': temp_senior_editors_map.get(manuscript[MANUSCRIPT_VERSION_ID], []),
      'reviewers': temp_reviewers_map.get(manuscript[MANUSCRIPT_VERSION_ID], []),
      'subject-areas': temp_subject_areas_map.get(manuscript[MANUSCRIPT_VERSION_ID], []),
    } for manuscript in manuscripts_all_list]
    self.manuscripts_by_version_id_map = dict((
      m[MANUSCRIPT_VERSION_ID], m) for m in manuscripts_all_list)
    manuscripts_by_doi_map = dict((
      m['doi'].lower(), m) for m in manuscripts_all_list if not is_null(m['doi']))
    debug("manuscripts_by_version_id_map:", self.manuscripts_by_version_id_map)

    self.manuscripts_by_author_map = {}
    self.manuscripts_by_reviewer_map = {}
    for m in manuscripts_all_list:
      if is_manuscript_relevant(m):
        for author in m['authors']:
          self.manuscripts_by_author_map.setdefault(author[PERSON_ID], [])\
          .append(m)
        for reviewer in m['reviewers']:
          self.manuscripts_by_reviewer_map.setdefault(reviewer[PERSON_ID], [])\
          .append(m)

    print("adding crossref data")
    for row in crossref_person_extras_df.to_dict(orient='records'):
      person_id = row[PERSON_ID]
      doi = row['doi'].lower()
      manuscript = manuscripts_by_doi_map.get(doi, None)
      if manuscript is None:
        manuscript = manuscript_by_crossref_person_extra(row)
        manuscripts_by_doi_map[doi] = manuscript
        self.manuscripts_by_version_id_map[
          manuscript[MANUSCRIPT_VERSION_ID]
        ] = manuscript
        self.manuscripts_by_author_map.setdefault(person_id, [])\
        .append(manuscript)

    self.manuscripts_by_author_map = applymap_dict(
      self.manuscripts_by_author_map, sort_manuscripts_by_date
    )
    self.manuscripts_by_reviewer_map = applymap_dict(
      self.manuscripts_by_reviewer_map, sort_manuscripts_by_date
    )

  def __find_manuscripts_by_keywords(self, keywords, manuscript_no=None):
    other_manuscripts = self.manuscript_keywords_df[
      self.manuscript_keywords_df['word'].isin(keywords)
    ]
    other_manuscripts = other_manuscripts[other_manuscripts[MANUSCRIPT_NO] != manuscript_no]
    other_manuscripts = groupby_agg_droplevel(
      other_manuscripts,
      MANUSCRIPT_ID_COLUMNS,
      {
        'word': {
          'keywords': lambda x: tuple(x),
          'count': pd.np.size
        }
      }
    )
    return other_manuscripts

  def __find_keywords_by_version_keys(self, version_ids):
    return self.manuscript_keywords_all_df[
      self.manuscript_keywords_all_df[MANUSCRIPT_VERSION_ID].isin(version_ids)
    ]['word']

  def __find_authors_by_manuscripts(self, manuscripts):
    other_authors = self.authors_df[self.authors_df[MANUSCRIPT_VERSION_ID].isin(
      manuscripts[MANUSCRIPT_VERSION_ID])]
    other_authors = other_authors[[MANUSCRIPT_VERSION_ID, 'author-person-id']].\
      drop_duplicates()
    other_authors = other_authors.rename(columns={
      'author-person-id': 'person-id'
    })
    return other_authors

  def __find_previous_reviewers_by_manuscripts(self, manuscripts):
    previous_reviewers = self.manuscript_history_review_received_df[
      self.manuscript_history_review_received_df[MANUSCRIPT_VERSION_ID].isin(
        manuscripts[MANUSCRIPT_VERSION_ID])]
    previous_reviewers = previous_reviewers[
      [MANUSCRIPT_VERSION_ID, 'stage-affective-person-id']].drop_duplicates()
    previous_reviewers = previous_reviewers.rename(columns={
      'stage-affective-person-id': 'person-id'
    })
    return previous_reviewers

  def __find_manuscripts_by_key(self, manuscript_no):
    return self.manuscript_versions_all_df[
      self.manuscript_versions_all_df[MANUSCRIPT_NO] == manuscript_no
    ].sort_values(VERSION_NO).groupby(MANUSCRIPT_NO).last()

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

  def _filter_manuscripts_by_subject_areas(self, manuscripts_df, subject_areas):
    df = manuscripts_df.merge(
      self.manuscript_subject_areas_df,
      how='inner',
      on=MANUSCRIPT_VERSION_ID
    )[[MANUSCRIPT_VERSION_ID, 'subject-area']]
    df = df[
      df['subject-area'].isin(subject_areas)
    ]
    return manuscripts_df[
      manuscripts_df[MANUSCRIPT_VERSION_ID].isin(
        df[MANUSCRIPT_VERSION_ID]
      )
    ]

  def _get_early_career_reviewer_ids_by_subject_areas(self, subject_areas):
    result = set(self.early_career_researchers_df[
      (
        self.early_career_researchers_df['First subject area'].isin(subject_areas) |
        self.early_career_researchers_df['Second subject area'].isin(subject_areas)
      ) &
      self.early_career_researchers_df[PERSON_ID].isin(self.persons_map)
    ][PERSON_ID].values)
    return result

  def get_all_subject_areas(self):
    return self.all_subject_areas

  def recommend(self, manuscript_no=None, subject_area=None, keywords=None, abstract=None, limit=None):
    keyword_list = self.__parse_keywords(keywords)
    exclude_person_ids = set()
    subject_areas = set()
    if subject_area is not None and len(subject_area) > 0:
      subject_areas.add(subject_area)
    matching_manuscripts_dicts = []
    manuscripts_not_found = None
    assigned_reviewers_by_person_id = {}
    if manuscript_no is not None and manuscript_no != '':
      matching_manuscripts = self.__find_manuscripts_by_key(manuscript_no)
      if len(matching_manuscripts) == 0:
        manuscripts_not_found = [manuscript_no]
      manuscript_keywords = self.__find_keywords_by_version_keys(
        matching_manuscripts[MANUSCRIPT_VERSION_ID])
      matching_manuscripts_dicts = map_to_dict(
        matching_manuscripts[MANUSCRIPT_VERSION_ID],
        self.manuscripts_by_version_id_map
      )
      keyword_list += list(manuscript_keywords.values)
      subject_areas = set(self.manuscript_subject_areas_all_df[
        self.manuscript_subject_areas_all_df[MANUSCRIPT_VERSION_ID].isin(
          matching_manuscripts[MANUSCRIPT_VERSION_ID]
        )
      ]['subject-area'])
      assigned_reviewers_by_person_id = groupby_to_dict(
        flatten([
          self.assigned_reviewers_by_manuscript_id_map.get(manuscript_id, [])
          for manuscript_id in matching_manuscripts[MANUSCRIPT_VERSION_ID].values
        ]),
        lambda item: item[PERSON_ID],
        lambda item: filter_dict_keys(item, lambda key: key != PERSON_ID)
      )
      print("assigned_reviewers_by_person_id:", assigned_reviewers_by_person_id)
      print("subject_areas:", subject_areas)
      authors = flatten([m['authors'] for m in matching_manuscripts_dicts])
      author_ids = [a[PERSON_ID] for a in authors]
      editors = flatten([m['editors'] for m in matching_manuscripts_dicts])
      editor_ids = [a[PERSON_ID] for a in editors]
      senior_editors = flatten([m['senior-editors'] for m in matching_manuscripts_dicts])
      senior_editor_ids = [a[PERSON_ID] for a in senior_editors]
      exclude_person_ids |= (set(author_ids) | set(editor_ids) | set(senior_editor_ids))
    else:
      matching_manuscripts = self.__find_manuscripts_by_key(None)
    print("keyword_list:", keyword_list)
    other_manuscripts = self.__find_manuscripts_by_keywords(
      keyword_list
    )
    print("subject_areas:", subject_areas)
    if len(subject_areas) > 0:
      other_manuscripts = self._filter_manuscripts_by_subject_areas(
        other_manuscripts, subject_areas
      )
    if abstract is not None and len(abstract.strip()) > 0:
      all_similar_manuscripts = self.similarity_model.find_similar_manuscripts_to_abstract(
        abstract
      )
    else:
      all_similar_manuscripts = self.similarity_model.find_similar_manuscripts(
        matching_manuscripts[MANUSCRIPT_VERSION_ID]
      )
    print("all_similar_manuscripts:", len(all_similar_manuscripts), all_similar_manuscripts[
      all_similar_manuscripts[MANUSCRIPT_VERSION_ID].isin(["10.1155/2013/435093"])
    ])
    similar_manuscripts = all_similar_manuscripts
    if len(subject_areas) > 0:
      similar_manuscripts = self._filter_manuscripts_by_subject_areas(
        similar_manuscripts, subject_areas
      )
    similarity_threshold = 0.5
    max_similarity_count = 50
    most_similar_manuscripts = similar_manuscripts[
      similar_manuscripts[SIMILARITY_COLUMN] >= similarity_threshold
    ]
    print("found {}/{} similar manuscripts beyond threshold {}".format(
      len(most_similar_manuscripts), len(similar_manuscripts),
      similarity_threshold
    ))
    if len(most_similar_manuscripts) > max_similarity_count:
      most_similar_manuscripts = most_similar_manuscripts\
      .sort_values(SIMILARITY_COLUMN, ascending=False)[:max_similarity_count]
    related_version_ids =\
      set(other_manuscripts[MANUSCRIPT_VERSION_ID].values) |\
      set(most_similar_manuscripts[MANUSCRIPT_VERSION_ID].values)
    other_manuscripts_dicts = [
      self.manuscripts_by_version_id_map.get(version_id)
      for version_id in related_version_ids
    ]
    other_manuscripts_dicts = [m for m in other_manuscripts_dicts if m]
    potential_reviewers_ids = (
      (set([
        person[PERSON_ID] for person in
        flatten([(m['authors'] + m['reviewers']) for m in other_manuscripts_dicts])
      ]) | self._get_early_career_reviewer_ids_by_subject_areas(
        subject_areas
      ) | assigned_reviewers_by_person_id.keys()) - exclude_person_ids
    )
    # print("potential_reviewers_ids", potential_reviewers_ids)
    # for m in other_manuscripts_dicts:
    #   print("author_ids", m[VERSION_KEY], [p[PERSON_ID] for p in m['authors']])

    keyword_match_count_by_by_version_key_map = {
      k: v['count']
      for k, v in other_manuscripts[[MANUSCRIPT_VERSION_ID, 'count']]\
      .set_index(MANUSCRIPT_VERSION_ID).to_dict(orient='index').items()
    }
    # print("keyword_match_count_by_by_version_key_map:", keyword_match_count_by_by_version_key_map)

    def populate_potential_reviewer(person_id):
      author_of_manuscripts = self.manuscripts_by_author_map.get(person_id, [])
      reviewer_of_manuscripts = self.manuscripts_by_reviewer_map.get(person_id, [])
      involved_manuscripts = author_of_manuscripts + reviewer_of_manuscripts

      total_keyword_match_count = float(sum([
        keyword_match_count_by_by_version_key_map.get(manuscript[MANUSCRIPT_VERSION_ID], 0)
        for manuscript in involved_manuscripts
      ]))

      max_similarity = null_to_none(all_similar_manuscripts[
        all_similar_manuscripts[MANUSCRIPT_VERSION_ID].isin(
          [m[MANUSCRIPT_VERSION_ID] for m in involved_manuscripts]
        )
      ][SIMILARITY_COLUMN].max())

      similarity_by_manuscript_version_id = all_similar_manuscripts[
        all_similar_manuscripts[MANUSCRIPT_VERSION_ID].isin(
          [m[MANUSCRIPT_VERSION_ID] for m in involved_manuscripts]
        )
      ].set_index(MANUSCRIPT_VERSION_ID)[SIMILARITY_COLUMN].to_dict()

      scores_by_manuscript = [
        {
          **manuscript_id_fields(manuscript),
          'keyword': keyword_match_count_by_by_version_key_map.get(
            manuscript[MANUSCRIPT_VERSION_ID], 0) / max(1, len(keyword_list)),
          'similarity': similarity_by_manuscript_version_id.get(
            manuscript[MANUSCRIPT_VERSION_ID], None)
        }
        for manuscript in involved_manuscripts
      ]

      if len(keyword_list) > 0:
        total_keyword_match_count = total_keyword_match_count / len(keyword_list)

      assignment_status = get_first(assigned_reviewers_by_person_id.get(person_id, []))

      potential_reviewer = {
        'person': self.persons_map.get(person_id, None),
        'author-of-manuscripts': author_of_manuscripts,
        'reviewer-of-manuscripts': reviewer_of_manuscripts,
        'scores': {
          'keyword': total_keyword_match_count,
          'similarity': max_similarity,
          'by-manuscript': scores_by_manuscript
        }
      }
      if assignment_status is not None:
        potential_reviewer['assignment-status'] = assignment_status
      return potential_reviewer

    potential_reviewers = [
      populate_potential_reviewer(person_id)
      for person_id in potential_reviewers_ids]

    review_duration_mean_keys = ['person', 'stats', 'overall', 'review-duration', 'mean']
    available_potential_reviewer_mean_durations = filter_none(deep_get_list(
      potential_reviewers, review_duration_mean_keys
    ))
    potential_reviewer_mean_duration = float(pd.np.mean(
      available_potential_reviewer_mean_durations))

    potential_reviewers = sorted(
      potential_reviewers,
      key=lambda potential_reviewer: (
        -potential_reviewer['scores']['keyword'],
        -(potential_reviewer['scores']['similarity'] or 0),
        deep_get(potential_reviewer, review_duration_mean_keys, potential_reviewer_mean_duration),
        potential_reviewer['person']['first-name'],
        potential_reviewer['person']['last-name']
      )
    )

    # create a list with interleaving normal reviewer, ecr, ...
    potential_reviewers = [x for x in itertools.chain.from_iterable(itertools.zip_longest(
      [pr for pr in potential_reviewers if not pr['person'].get('is-early-career-researcher')],
      [pr for pr in potential_reviewers if pr['person'].get('is-early-career-researcher')]
    )) if x]

    if limit is not None and limit > 0:
      potential_reviewers = potential_reviewers[:limit]

    result = {
      'potential-reviewers': potential_reviewers,
      'matching-manuscripts': map_to_dict(
        matching_manuscripts[MANUSCRIPT_VERSION_ID],
        self.manuscripts_by_version_id_map
      )
    }
    if manuscripts_not_found is not None:
      result['manuscripts-not-found'] = manuscripts_not_found
    return result
