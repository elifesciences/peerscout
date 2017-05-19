from itertools import groupby
import itertools
import ast
import logging

import pandas as pd

from .utils import unescape_and_strip_tags, filter_by

from .collection_utils import (
  flatten,
  filter_none,
  deep_get,
  deep_get_list
)

NAME = 'RecommendReviewers'

debugv_enabled = False

def set_debugv_enabled(enabled):
  global debugv_enabled
  debugv_enabled = enabled

def debugv(*args):
  if debugv_enabled:
    logging.getLogger(NAME).debug(*args)

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
  return not isinstance(x, list) and (pd.isnull(x) or is_nat(x))

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
  get_groupby_key = lambda x: x[0]
  return {
    k: [
      item for item in [
        vf(version_key) for version_key in
        set([version_key for _, version_key in list(v)])
      ] if item
    ]
    for k, v in groupby(sorted(
      zip(groupby_keys, version_keys),
      key=get_groupby_key
    ), get_groupby_key)
  }

def filter_dict_keys(d, f):
  return {k: v for k, v in d.items() if f(k)}

def groupby_column_to_dict(df, groupby_col, value_col=None, sort_by=None):
  if value_col is None:
    value_f = lambda item: filter_dict_keys(item, lambda col: col != groupby_col)
  elif callable(value_col):
    value_f = value_col
  else:
    value_f = lambda item: item[value_col]
  if sort_by is None:
    sort_by = groupby_col
  a = df.sort_values(sort_by).to_dict(orient='records')
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

MANUSCRIPT_ID = 'manuscript_id'
VERSION_ID = 'version_id'

RAW_MANUSCRIPT_ID_COLUMNS = []
TEMP_MANUSCRIPT_ID_COLUMNS = [VERSION_ID]
MANUSCRIPT_ID_COLUMNS = RAW_MANUSCRIPT_ID_COLUMNS + TEMP_MANUSCRIPT_ID_COLUMNS

SIMILARITY_COLUMN = 'similarity'

PERSON_ID = 'person_id'

PERSON_COLUMNS = [
  PERSON_ID,
  'title', 'first_name', 'middle_name', 'last_name', 'institution', 'status', 'email',
  'is_early_career_researcher'
]

def unescape_if_string(s):
  if isinstance(s, str):
    return unescape_and_strip_tags(s)
  return s

def stats_by_person_for_period(table):
  df = table.read_frame()
  debugv("person stats frame (%s):\n%s", table.table.__tablename__, df)
  if len(df) == 0:
    return {}

  def get_review_duration_details(v):
    if v['reviewed_count'] == 0:
      return
    return {
      'min': v['reviewed_duration_min'],
      'max': v['reviewed_duration_max'],
      'mean': v['reviewed_duration_avg'],
      'count': v['reviewed_count']
    }

  m = clean_result({
    k: {
      'review_duration': get_review_duration_details(v),
      'reviews_in_progress': v['awaiting_review_count'],
      'waiting_to_be_accepted': v['awaiting_accept_count'],
      'declined': v['declined_count']
    }
    for k, v in df.to_dict(orient='index').items()
  })
  debugv("person stats map:\n%s", m)
  return m

def select_dict_keys(d, keys):
  return {k: d[k] for k in keys}

def manuscript_id_fields(manuscript):
  return select_dict_keys(manuscript, MANUSCRIPT_ID_COLUMNS)

def sort_manuscripts_by_date(manuscripts):
  return sorted(manuscripts, key=lambda m: (
    m.get('published-date', None),
    m.get('title', None),
    m.get(VERSION_ID, None)
  ), reverse=True)

def parse_list_if_str(x):
  if isinstance(x, str):
    return ast.literal_eval(x)
  return x

class RecommendReviewers(object):
  def __init__(self, db, manuscript_model, similarity_model=None):
    logger = logging.getLogger(NAME)
    self.logger = logger
    self.similarity_model = similarity_model

    self.manuscript_versions_all_df = (
      db.manuscript_version.read_frame().reset_index()
      .rename(columns={'id': VERSION_ID})
    )

    valid_version_ids = manuscript_model.get_valid_manuscript_version_ids()

    self.manuscript_versions_df = filter_by(
      self.manuscript_versions_all_df,
      VERSION_ID,
      valid_version_ids
    )

    self.manuscript_keywords_all_df = (
      db.manuscript_keyword.read_frame().reset_index()
    )

    self.manuscript_keywords_df = filter_by(
      self.manuscript_keywords_all_df,
      VERSION_ID,
      valid_version_ids
    )

    self.authors_all_df = (
      db.manuscript_author.read_frame().reset_index()
    )

    self.editors_all_df = (
      db.manuscript_editor.read_frame().reset_index()
    )

    self.senior_editors_all_df = (
      db.manuscript_senior_editor.read_frame().reset_index()
    )

    self.manuscript_history_all_df = (
      db.manuscript_stage.read_frame().reset_index()
    )

    self.manuscript_history_df = filter_by(
      self.manuscript_history_all_df,
      VERSION_ID,
      valid_version_ids
    )

    self.manuscript_subject_areas_all_df = (
      db.manuscript_subject_area.read_frame().reset_index()
    )

    self.manuscript_subject_areas_df = filter_by(
      self.manuscript_subject_areas_all_df,
      VERSION_ID,
      valid_version_ids
    )

    manuscripts_df = (
      db.manuscript.read_frame().reset_index()
      .rename(columns={'id': MANUSCRIPT_ID})
    )

    self.persons_df = (
      db.person.read_frame().reset_index()
      .rename(columns={'id': PERSON_ID})
    )

    memberships_df = (
      db.person_membership.read_frame()
      .rename(columns={'person_id': PERSON_ID})
    )

    dates_not_available_df = (
      db.person_dates_not_available.read_frame().reset_index()
      .rename(columns={'person_id': PERSON_ID})
    )

    dates_not_available_df = dates_not_available_df[
      dates_not_available_df['end_date'] >= pd.to_datetime('today')
    ]

    self.manuscript_history_review_received_df = filter_by(
      self.manuscript_history_df,
      'stage_name',
      ['Review Received']
    )

    self.assigned_reviewers_df = (
      db.manuscript_potential_reviewer.read_frame().reset_index()
      .rename(columns={'version_id': VERSION_ID})
    )

    temp_memberships_map = groupby_column_to_dict(memberships_df, PERSON_ID)
    dates_not_available_map = groupby_column_to_dict(dates_not_available_df, PERSON_ID)
    # early_career_researchers_person_ids = set(early_career_researchers_df[PERSON_ID].values)

    logger.debug("gathering stats")
    overall_stats_map = stats_by_person_for_period(db.person_review_stats_overall)
    last12m_stats_map = stats_by_person_for_period(db.person_review_stats_last12m)

    logger.debug("building person list")
    persons_list = [{
      **person,
      # 'is-early-career-researcher': person['person-id'] in early_career_researchers_person_ids,
      'memberships': temp_memberships_map.get(person[PERSON_ID], []),
      'dates_not_available': dates_not_available_map.get(person[PERSON_ID], []),
      'stats': {
        'overall': overall_stats_map.get(person[PERSON_ID], None),
        'last_12m': last12m_stats_map.get(person[PERSON_ID], None)
      }
    } for person in clean_result(self.persons_df[PERSON_COLUMNS].to_dict(orient='records'))]

    self.persons_map = dict((p[PERSON_ID], p) for p in persons_list)

    debugv("self.persons_df: %s", self.persons_df)
    debugv("persons_map: %s", self.persons_map)

    temp_authors_map = groupby_column_to_dict(
      self.authors_all_df,
      VERSION_ID,
      lambda author: {
        **self.persons_map.get(author[PERSON_ID], None),
        'is_corresponding_author': author['is_corresponding_author']
      },
      sort_by=[VERSION_ID, 'seq']
    )

    temp_editors_map = groupby_columns_to_dict(
      self.editors_all_df[VERSION_ID].values,
      self.editors_all_df[PERSON_ID].values,
      lambda person_id: self.persons_map.get(person_id, None)
    )

    temp_senior_editors_map = groupby_columns_to_dict(
      self.senior_editors_all_df[VERSION_ID].values,
      self.senior_editors_all_df[PERSON_ID].values,
      lambda person_id: self.persons_map.get(person_id, None)
    )

    temp_reviewers_map = groupby_columns_to_dict(
      self.manuscript_history_review_received_df[VERSION_ID].values,
      self.manuscript_history_review_received_df[PERSON_ID].values,
      lambda person_id: self.persons_map.get(person_id, None)
    )

    self.assigned_reviewers_by_manuscript_id_map = groupby_column_to_dict(
      self.assigned_reviewers_df,
      VERSION_ID,
      lambda row: dict({
        PERSON_ID: row[PERSON_ID],
        'status': row['status'],
        'excluded': row['suggested_to_exclude'] == 'yes'
      })
    )

    debugv(
      "self.manuscript_history_review_received_df: %s", self.manuscript_history_review_received_df
    )
    debugv("temp_authors_map: %s", temp_authors_map)
    debugv("temp_reviewers_map: %s", temp_reviewers_map)

    temp_doi_by_manuscript_no_map = groupby_column_to_dict(
      manuscripts_df,
      MANUSCRIPT_ID,
      'doi')

    self.all_subject_areas = sorted(set(self.manuscript_subject_areas_all_df['subject_area']))
    temp_subject_areas_map = groupby_column_to_dict(
      self.manuscript_subject_areas_all_df,
      VERSION_ID,
      'subject_area'
    )

    self.all_keywords = sorted(set(self.manuscript_keywords_df['keyword']))

    logger.debug("building manuscript list")
    manuscripts_all_list = clean_result(
      self.manuscript_versions_all_df[
        MANUSCRIPT_ID_COLUMNS +
        [MANUSCRIPT_ID] +
        ['title', 'decision', 'manuscript_type', 'abstract', 'decision_timestamp']
      ].rename(columns={'decision-date': 'published-date'})
      .to_dict(orient='records'))
    manuscripts_all_list = [{
      **manuscript,
      'doi': get_first(temp_doi_by_manuscript_no_map.get(manuscript[MANUSCRIPT_ID], [])),
      'authors': temp_authors_map.get(manuscript[VERSION_ID], []),
      'editors': temp_editors_map.get(manuscript[VERSION_ID], []),
      'senior_editors': temp_senior_editors_map.get(manuscript[VERSION_ID], []),
      'reviewers': temp_reviewers_map.get(manuscript[VERSION_ID], []),
      'subject_areas': temp_subject_areas_map.get(manuscript[VERSION_ID], []),
    } for manuscript in manuscripts_all_list]
    self.manuscripts_by_version_id_map = dict((
      m[VERSION_ID], m) for m in manuscripts_all_list)
    debugv("manuscripts_by_version_id_map: %s", self.manuscripts_by_version_id_map)

    self.manuscripts_by_author_map = {}
    self.manuscripts_by_reviewer_map = {}
    for m in manuscripts_all_list:
      if manuscript_model.is_manuscript_relevant(m):
        debugv("manuscript: %s", m)
        for author in m['authors']:
          self.manuscripts_by_author_map.setdefault(author[PERSON_ID], [])\
          .append(m)
        for reviewer in m['reviewers']:
          self.manuscripts_by_reviewer_map.setdefault(reviewer[PERSON_ID], [])\
          .append(m)
      else:
        debugv("ignoring manuscript: %s", m)

    self.manuscripts_by_author_map = applymap_dict(
      self.manuscripts_by_author_map, sort_manuscripts_by_date
    )

    self.manuscripts_by_reviewer_map = applymap_dict(
      self.manuscripts_by_reviewer_map, sort_manuscripts_by_date
    )

    debugv("manuscripts_by_author_map: %s", self.manuscripts_by_author_map)
    debugv("manuscripts_by_reviewer_map: %s", self.manuscripts_by_reviewer_map)

    early_career_researcher_person_id_query = db.session.query(
      db.person.table.person_id
    ).filter(
      db.person.table.is_early_career_researcher == True # pylint: disable=C0121
    )

    self.early_career_researcher_ids_by_subject_area = groupby_to_dict(
      db.session.query(
        db.person_subject_area.table.subject_area,
        db.person_subject_area.table.person_id
      ).filter(
        db.person_subject_area.table.person_id.in_(
          early_career_researcher_person_id_query
        )
      ).all(),
      lambda row: row[0].lower(),
      lambda row: row[1]
    )
    debugv(
      "early career researcher subject area keys: %s",
      self.early_career_researcher_ids_by_subject_area.keys())

  def __find_manuscripts_by_keywords(self, keywords):
    other_manuscripts = self.manuscript_keywords_df[
      self.manuscript_keywords_df['keyword'].isin(keywords)
    ]
    other_manuscripts = groupby_agg_droplevel(
      other_manuscripts,
      MANUSCRIPT_ID_COLUMNS,
      {
        'keyword': {
          'keywords': lambda x: tuple(x),
          'count': pd.np.size
        }
      }
    )
    return other_manuscripts

  def __find_keywords_by_version_keys(self, version_ids):
    return self.manuscript_keywords_all_df[
      self.manuscript_keywords_all_df[VERSION_ID].isin(version_ids)
    ]['keyword']

  def __find_manuscripts_by_key(self, manuscript_no):
    return self.manuscript_versions_all_df[
      self.manuscript_versions_all_df[MANUSCRIPT_ID] == manuscript_no
    ].sort_values(VERSION_ID).groupby(MANUSCRIPT_ID).last()

  def __parse_keywords(self, keywords):
    keywords = (keywords or '').strip()
    if keywords == '':
      return []
    return [keyword.strip() for keyword in keywords.split(',')]

  def _filter_manuscripts_by_subject_areas(self, manuscripts_df, subject_areas):
    df = manuscripts_df.merge(
      self.manuscript_subject_areas_df,
      how='inner',
      on=VERSION_ID
    )[[VERSION_ID, 'subject_area']]
    df = df[
      df['subject_area'].isin(subject_areas)
    ]
    return manuscripts_df[
      manuscripts_df[VERSION_ID].isin(
        df[VERSION_ID]
      )
    ]

  def _get_early_career_reviewer_ids_by_subject_areas(self, subject_areas):
    result = set(flatten([
      self.early_career_researcher_ids_by_subject_area.get(subject_area.lower(), [])
      for subject_area in subject_areas
    ]))
    self.logger.debug(
      "found %d early career researchers for subject areas: %s", len(result), subject_areas
    )
    return result

  def get_all_subject_areas(self):
    return self.all_subject_areas

  def get_all_keywords(self):
    return self.all_keywords

  def recommend(
    self, manuscript_no=None, subject_area=None, keywords=None, abstract=None, limit=None
    ):
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
        matching_manuscripts[VERSION_ID])
      matching_manuscripts_dicts = map_to_dict(
        matching_manuscripts[VERSION_ID],
        self.manuscripts_by_version_id_map
      )
      keyword_list += list(manuscript_keywords.values)
      subject_areas = set(self.manuscript_subject_areas_all_df[
        self.manuscript_subject_areas_all_df[VERSION_ID].isin(
          matching_manuscripts[VERSION_ID]
        )
      ]['subject_area'])
      assigned_reviewers_by_person_id = groupby_to_dict(
        flatten([
          self.assigned_reviewers_by_manuscript_id_map.get(manuscript_id, [])
          for manuscript_id in matching_manuscripts[VERSION_ID].values
        ]),
        lambda item: item[PERSON_ID],
        lambda item: filter_dict_keys(item, lambda key: key != PERSON_ID)
      )
      self.logger.debug("assigned_reviewers_by_person_id: %s", assigned_reviewers_by_person_id)
      self.logger.debug("subject_areas: %s", subject_areas)
      authors = flatten([m['authors'] for m in matching_manuscripts_dicts])
      author_ids = [a[PERSON_ID] for a in authors]
      editors = flatten([m['editors'] for m in matching_manuscripts_dicts])
      editor_ids = [a[PERSON_ID] for a in editors]
      senior_editors = flatten([m['senior_editors'] for m in matching_manuscripts_dicts])
      senior_editor_ids = [a[PERSON_ID] for a in senior_editors]
      exclude_person_ids |= (set(author_ids) | set(editor_ids) | set(senior_editor_ids))
    else:
      matching_manuscripts = self.__find_manuscripts_by_key(None)
    self.logger.debug("keyword_list: %s", keyword_list)
    other_manuscripts = self.__find_manuscripts_by_keywords(
      keyword_list
    )
    self.logger.debug("subject_areas: %s", subject_areas)
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
        matching_manuscripts[VERSION_ID]
      )
    self.logger.debug(
      "all_similar_manuscripts: %d, %s",
      len(all_similar_manuscripts),
      all_similar_manuscripts[
        all_similar_manuscripts[VERSION_ID].isin(["10.1155/2013/435093"])
      ]
    )
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
    self.logger.debug(
      "found %d/%d similar manuscripts beyond threshold %f",
      len(most_similar_manuscripts),
      len(similar_manuscripts),
      similarity_threshold
    )
    if len(most_similar_manuscripts) > max_similarity_count:
      most_similar_manuscripts = most_similar_manuscripts\
      .sort_values(SIMILARITY_COLUMN, ascending=False)[:max_similarity_count]
    related_version_ids =\
      set(other_manuscripts[VERSION_ID].values) |\
      set(most_similar_manuscripts[VERSION_ID].values)
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

    keyword_match_count_by_by_version_key_map = {
      k: v['count']
      for k, v in other_manuscripts[[VERSION_ID, 'count']]\
      .set_index(VERSION_ID).to_dict(orient='index').items()
    }

    def populate_potential_reviewer(person_id):
      author_of_manuscripts = self.manuscripts_by_author_map.get(person_id, [])
      reviewer_of_manuscripts = self.manuscripts_by_reviewer_map.get(person_id, [])
      involved_manuscripts = author_of_manuscripts + reviewer_of_manuscripts

      similarity_by_manuscript_version_id = all_similar_manuscripts[
        all_similar_manuscripts[VERSION_ID].isin(
          [m[VERSION_ID] for m in involved_manuscripts]
        )
      ].set_index(VERSION_ID)[SIMILARITY_COLUMN].to_dict()

      def score_by_manuscript(manuscript, keyword, similarity):
        return {
          **manuscript_id_fields(manuscript),
          'keyword': keyword,
          'similarity': similarity,
          'combined': min(1.0, keyword + (similarity or 0) * 0.5)
        }

      scores_by_manuscript = [
        score_by_manuscript(
          manuscript,
          keyword=keyword_match_count_by_by_version_key_map.get(
            manuscript[VERSION_ID], 0) / max(1, len(keyword_list)),
          similarity=similarity_by_manuscript_version_id.get(
            manuscript[VERSION_ID], None)
        )
        for manuscript in involved_manuscripts
      ]
      scores_by_manuscript = list(reversed(sorted(scores_by_manuscript, key=lambda score: (
        score['combined'],
        score['keyword'],
        score['similarity']
      ))))
      best_score = get_first(scores_by_manuscript, {})

      assignment_status = get_first(assigned_reviewers_by_person_id.get(person_id, []))

      potential_reviewer = {
        'person': self.persons_map.get(person_id, None),
        'author_of_manuscripts': author_of_manuscripts,
        'reviewer_of_manuscripts': reviewer_of_manuscripts,
        'scores': {
          'keyword': best_score.get('keyword'),
          'similarity': best_score.get('similarity'),
          'combined': best_score.get('combined'),
          'by_manuscript': scores_by_manuscript
        }
      }
      if assignment_status is not None:
        potential_reviewer['assignment_status'] = assignment_status
      return potential_reviewer

    potential_reviewers = [
      populate_potential_reviewer(person_id)
      for person_id in potential_reviewers_ids]

    review_duration_mean_keys = ['person', 'stats', 'overall', 'review-duration', 'mean']
    available_potential_reviewer_mean_durations = filter_none(deep_get_list(
      potential_reviewers, review_duration_mean_keys
    ))
    potential_reviewer_mean_duration = (
      float(pd.np.mean(available_potential_reviewer_mean_durations))
      if len(available_potential_reviewer_mean_durations) > 0
      else None
    )

    potential_reviewers = sorted(
      potential_reviewers,
      key=lambda potential_reviewer: (
        -(potential_reviewer['scores'].get('combined') or 0),
        -(potential_reviewer['scores'].get('keyword') or 0),
        -(potential_reviewer['scores'].get('similarity') or 0),
        deep_get(potential_reviewer, review_duration_mean_keys, potential_reviewer_mean_duration),
        potential_reviewer['person']['first_name'],
        potential_reviewer['person']['last_name']
      )
    )

    # create a list with interleaving normal reviewer, ecr, ...
    potential_reviewers = [x for x in itertools.chain.from_iterable(itertools.zip_longest(
      [pr for pr in potential_reviewers if not pr['person'].get('is_early_career_researcher')],
      [pr for pr in potential_reviewers if pr['person'].get('is_early_career_researcher')]
    )) if x]

    if limit is not None and limit > 0:
      potential_reviewers = potential_reviewers[:limit]

    result = {
      'potential_reviewers': potential_reviewers,
      'matching_manuscripts': map_to_dict(
        matching_manuscripts[VERSION_ID],
        self.manuscripts_by_version_id_map
      )
    }
    if manuscripts_not_found is not None:
      result['manuscripts_not_found'] = manuscripts_not_found
    elif len(matching_manuscripts) == 0:
      result['search'] = remove_none({
        'subject_area': subject_area,
        'keywords': keyword_list,
        'abstract': abstract
      })
    return result
