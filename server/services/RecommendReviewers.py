from itertools import groupby
import ast
from datetime import datetime

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from .utils import unescape_and_strip_tags

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

def groupby_column_to_dict(df, groupby_col, value_col=None):
  if value_col is None:
    value_f = lambda item: filter_dict_keys(item, lambda col: col != groupby_col)
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

ABSTRACT_DOCVEC_COLUMN = 'abstract-docvec'
SIMILARITY_COLUMN = 'similarity'

PERSON_ID = 'person-id'

PERSON_COLUMNS = [
  'person-id',
  'title', 'first-name', 'middle-name', 'last-name', 'institution', 'status'
]

DECISIONS_ACCEPTED = set(['Accept Full Submission', 'Auto-Accept'])
TYPES_ACCEPTED = set([
  'Research Article', 'Short Report', 'Tools and Resources', 'Research Advance'
])

def filter_accepted_manuscript_versions(manuscript_versions):
  return manuscript_versions[
    manuscript_versions['decision'].isin(DECISIONS_ACCEPTED)
  ]

def filter_research_articles(manuscript_versions):
  print("manuscript types:", manuscript_versions['manuscript-type'].unique())
  return manuscript_versions[
    manuscript_versions['manuscript-type'].isin(
      ['Research Article', 'Initial Submission: Research Article'])
  ]

def is_manuscript_accepted(manuscript):
  return manuscript.get('decision', None) in DECISIONS_ACCEPTED

def is_manuscript_type_relevant(manuscript):
  return manuscript.get('manuscript-type') in TYPES_ACCEPTED

def is_manuscript_relevant(manuscript):
  return is_manuscript_accepted(manuscript) and is_manuscript_type_relevant(manuscript)

def filter_by(df, col_name, values):
  return df[df[col_name].isin(values)]

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
    'first-name': early_career_reviewer['first-name'],
    'last-name': early_career_reviewer['last-name'],
    'is-early-career-reviewer': True,
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

def manuscript_by_crossref_person_extra(crossref_person_extra):
  doi = crossref_person_extra['doi']
  return {
    MANUSCRIPT_VERSION_ID: doi,
    MANUSCRIPT_NO: doi,
    VERSION_NO: None,
    'doi': doi,
    'title': crossref_person_extra['title'],
    'abstract': crossref_person_extra['abstract'],
    'subject-areas': ast.literal_eval(crossref_person_extra['subject-areas']),
    'published-date': crossref_person_extra['created-date']
  }

class RecommendReviewers(object):
  def __init__(self, datasets):
    self.manuscript_versions_all_df = add_manuscript_version_id(
      datasets['manuscript-versions'].copy())
    for c in ['title', 'abstract']:
      self.manuscript_versions_all_df[c] = self.manuscript_versions_all_df[c].apply(
        unescape_if_string
      )
    self.manuscript_versions_df = filter_research_articles(filter_accepted_manuscript_versions(
      self.manuscript_versions_all_df
    ))
    print("manuscript_versions_df:", self.manuscript_versions_df.shape)
    self.manuscript_last_versions_df = self.manuscript_versions_df\
      .sort_values(VERSION_NO)\
      .groupby([MANUSCRIPT_NO], as_index=False)\
      .last()
    valid_version_ids = self.manuscript_last_versions_df[MANUSCRIPT_VERSION_ID]
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

    self.abstract_docvecs_all_df = add_manuscript_version_id(
      datasets["manuscript-abstracts-spacy-docvecs"]\
      .rename(columns={'abstract-spacy-docvecs': ABSTRACT_DOCVEC_COLUMN}).dropna())
    self.abstract_docvecs_df = filter_by(
      self.abstract_docvecs_all_df,
      MANUSCRIPT_VERSION_ID,
      valid_version_ids
    )
    print("valid docvecs:", len(self.abstract_docvecs_df))

    crossref_abstract_docvecs_df = (
      datasets["crossref-person-extra-spacy-docvecs"]
      .rename(columns={
        'abstract-spacy-docvecs': ABSTRACT_DOCVEC_COLUMN,
        'doi': MANUSCRIPT_VERSION_ID
      }).dropna()
    )
    crossref_abstract_docvecs_df[MANUSCRIPT_VERSION_ID] = (
      crossref_abstract_docvecs_df[MANUSCRIPT_VERSION_ID].str.lower()
    )
    self.abstract_docvecs_df = pd.concat([
      self.abstract_docvecs_df,
      crossref_abstract_docvecs_df
    ])
    print("docvecs incl crossref:", len(self.abstract_docvecs_df))

    self.persons_df = datasets["persons"].copy()
    early_career_reviewers_df = datasets["early-career-reviewers"]
    self.early_career_reviewers_df = early_career_reviewers_df
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
    early_career_reviewers_person_ids = set(early_career_reviewers_df[PERSON_ID].values)

    stage_pivot = create_stage_pivot(self.manuscript_history_all_df)
    overall_stats_map = stats_by_person_for_period(stage_pivot)

    # review_durations_map = duration_stats_between_by_person(
    #   stage_pivot, 'Reviewers Accept', 'Review Received').to_dict(orient='index')
    today = datetime.today()
    from_12m = pd.Timestamp(today.replace(year=today.year - 1))
    last12m_stats_map = stats_by_person_for_period(stage_pivot, lambda dt: dt >= from_12m)
    # review_durations_last12m_map = duration_stats_between_by_person(
    #   filter_stage_pivot_by_stage(stage_pivot, 'Review Received', lambda dt: dt >= from_12m),
    #   'Reviewers Accept', 'Review Received').to_dict(orient='index')

    persons_list = [{
      **person,
      'is-early-career-reviewer': person['person-id'] in early_career_reviewers_person_ids,
      'memberships': temp_memberships_map.get(person['person-id'], []),
      'dates-not-available': dates_not_available_map.get(person['person-id'], []),
      'stats': {
        'overall': overall_stats_map.get(person['person-id'], None),
        'last-12m': last12m_stats_map.get(person['person-id'], None)
      }
    } for person in clean_result(self.persons_df[PERSON_COLUMNS].to_dict(orient='records'))]

    self.persons_map = dict((p[PERSON_ID], p) for p in persons_list)

    for row in early_career_reviewers_df.to_dict(orient='records'):
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

    temp_reviewers_map = groupby_columns_to_dict(
      self.manuscript_history_review_received_df[MANUSCRIPT_VERSION_ID].values,
      self.manuscript_history_review_received_df['stage-affective-person-id'].values,
      lambda person_id: self.persons_map.get(person_id, None)
    )
    debug("self.manuscript_history_review_received_df:", self.manuscript_history_review_received_df)
    debug("temp_authors_map:", temp_authors_map)
    debug("temp_reviewers_map:", temp_reviewers_map)

    temp_doi_by_manuscript_no_map = groupby_column_to_dict(
      manuscripts_df,
      MANUSCRIPT_NO,
      'production-data-doi')

    temp_subject_areas_map = groupby_column_to_dict(
      self.manuscript_subject_areas_all_df,
      MANUSCRIPT_VERSION_ID,
      'subject-area'
    )

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

  def __find_similar_manuscripts(self, version_ids):
    to_docvecs = self.abstract_docvecs_all_df[
      self.abstract_docvecs_all_df[MANUSCRIPT_VERSION_ID].isin(
        version_ids
      )
    ][ABSTRACT_DOCVEC_COLUMN].values
    if len(to_docvecs) == 0:
      print("no docvecs for:", version_ids)
      return pd.DataFrame({
        MANUSCRIPT_VERSION_ID: [],
        SIMILARITY_COLUMN: []
      })
    all_docvecs = self.abstract_docvecs_df[ABSTRACT_DOCVEC_COLUMN].values
    to_docvecs = to_docvecs.tolist()
    all_docvecs = all_docvecs.tolist()
    similarity = pd.DataFrame({
      MANUSCRIPT_VERSION_ID: self.abstract_docvecs_df[MANUSCRIPT_VERSION_ID],
      SIMILARITY_COLUMN: cosine_similarity(
        all_docvecs,\
        to_docvecs
      )[:, 0]
    })
    similarity = similarity[
      ~similarity[MANUSCRIPT_VERSION_ID].isin(
        version_ids
      )
    ]
    return similarity

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
    result = set(self.early_career_reviewers_df[
      (
        self.early_career_reviewers_df['First subject area'].isin(subject_areas) |
        self.early_career_reviewers_df['Second subject area'].isin(subject_areas)
      ) &
      self.early_career_reviewers_df[PERSON_ID].isin(self.persons_map)
    ][PERSON_ID].values)
    return result

  def recommend(self, keywords, manuscript_no):
    keyword_list = self.__parse_keywords(keywords)
    exclude_person_ids = set()
    subject_areas = set()
    matching_manuscripts_dicts = []
    if manuscript_no is not None and manuscript_no != '':
      matching_manuscripts = self.__find_manuscripts_by_key(manuscript_no)
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
      print("subject_areas:", subject_areas)
      authors = flatten([m['authors'] for m in matching_manuscripts_dicts])
      author_ids = [a[PERSON_ID] for a in authors]
      exclude_person_ids |= set(author_ids)
    else:
      matching_manuscripts = self.__find_manuscripts_by_key(None)
    print("keyword_list:", keyword_list)
    other_manuscripts = self.__find_manuscripts_by_keywords(
      keyword_list
    )
    if len(subject_areas) > 0:
      other_manuscripts = self._filter_manuscripts_by_subject_areas(
        other_manuscripts, subject_areas
      )
    all_similar_manuscripts = self.__find_similar_manuscripts(
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
      )) - exclude_person_ids
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

      return {
        'person': self.persons_map.get(person_id, None),
        'author-of-manuscripts': author_of_manuscripts,
        'reviewer-of-manuscripts': reviewer_of_manuscripts,
        'scores': {
          'keyword': total_keyword_match_count,
          'similarity': max_similarity,
          'by-manuscript': scores_by_manuscript
        }
      }

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

    return {
      'potential-reviewers': potential_reviewers,
      'matching-manuscripts': map_to_dict(
        matching_manuscripts[MANUSCRIPT_VERSION_ID],
        self.manuscripts_by_version_id_map
      )
    }
