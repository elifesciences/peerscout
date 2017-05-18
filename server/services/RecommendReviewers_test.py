"""
Unit test
"""
import pprint
import logging

import pandas as pd
import sqlalchemy

from shared_proxy import database

from .ManuscriptModel import ManuscriptModel
from .DocumentSimilarityModel import DocumentSimilarityModel
from .RecommendReviewers import RecommendReviewers, set_debugv_enabled

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger('test')

set_debugv_enabled(True)

MANUSCRIPT_ID = 'manuscript_id'
VERSION_ID = 'version_id'

PERSON_ID = 'person_id'

MANUSCRIPT_ID_COLUMNS = [VERSION_ID]
PERSON_ID_COLUMNS = [PERSON_ID]

MANUSCRIPT_AUTHOR = pd.DataFrame(
  [],
  columns=MANUSCRIPT_ID_COLUMNS + [PERSON_ID]
)

MANUSCRIPT_EDITOR = pd.DataFrame(
  [],
  columns=MANUSCRIPT_ID_COLUMNS + [PERSON_ID]
)

MANUSCRIPT_SENIOR_EDITOR = pd.DataFrame(
  [],
  columns=MANUSCRIPT_ID_COLUMNS + [PERSON_ID]
)

MANUSCRIPT_POTENTIAL_REVIEWER = pd.DataFrame(
  [],
  columns=MANUSCRIPT_ID_COLUMNS + [
    PERSON_ID,
    'status',
    'suggested_to_exclude'
  ]
)

PERSON = pd.DataFrame(
  [],
  columns=PERSON_ID_COLUMNS + [
    'title', 'first_name', 'middle_name', 'last_name', 'institution', 'status', 'email',
    'is_early_career_researcher'
  ]
)

PERSON_MEMBERSHIP = pd.DataFrame(
  [],
  columns=PERSON_ID_COLUMNS + [
    'member_type', 'member_id'
  ]
)

PERSON_DATES_NOT_AVAILABLE = pd.DataFrame(
  [],
  columns=PERSON_ID_COLUMNS + [
    'start_date', 'end_date'
  ]
)

PERSON_SUBJECT_AREA = pd.DataFrame(
  [],
  columns=PERSON_ID_COLUMNS + ['subject_area']
)

MANUSCRIPT = pd.DataFrame(
  [],
  columns=[MANUSCRIPT_ID]
)

MANUSCRIPT_VERSION = pd.DataFrame(
  [],
  columns=MANUSCRIPT_ID_COLUMNS + [
    MANUSCRIPT_ID,
    'title', 'decision', 'manuscript_type', 'abstract',
    'decision_timestamp'
  ]
)

MANUSCRIPT_KEYWORD = pd.DataFrame(
  [],
  columns=MANUSCRIPT_ID_COLUMNS + ['keyword']
)

MANUSCRIPT_SUBJECT_AREAS = pd.DataFrame(
  [],
  columns=MANUSCRIPT_ID_COLUMNS + ['subject_area']
)

MANUSCRIPT_STAGE = pd.DataFrame(
  [],
  columns=MANUSCRIPT_ID_COLUMNS + [PERSON_ID, 'stage_name', 'stage_timestamp'])

LDA_DOCVEC_COLUMN = 'lda_docvec'
DOC2VEC_DOCVEC_COLUMN = 'doc2vec_docvec'

ML_MANUSCRIPT_DATA = pd.DataFrame(
  [],
  columns=MANUSCRIPT_ID_COLUMNS + [LDA_DOCVEC_COLUMN, DOC2VEC_DOCVEC_COLUMN])

ML_MANUSCRIPT_DATA_DATASET = 'ml_manuscript_data'
SUBJECT_AREAS_DATASET = 'manuscript_subject_area'

DATASETS = {
}

PERSON_ID1 = 'person1'
PERSON_ID2 = 'person2'
PERSON_ID3 = 'person3'

PERSON1 = {
  PERSON_ID: PERSON_ID1,
  'first_name': 'John',
  'last_name': 'Smith',
  'status': 'Active',
  'is_early_career_researcher': False
}

PERSON1_RESULT = {
  **PERSON1,
  'memberships': [],
  'dates_not_available': [],
  'stats': {
    'overall': None,
    'last_12m': None
  }
}

PERSON2 = {
  **PERSON1,
  PERSON_ID: PERSON_ID2,
  'first-name': 'Laura',
  'last-name': 'Laudson'
}

PERSON2_RESULT = {
  **PERSON1_RESULT,
  **PERSON2
}

PERSON3 = {
  **PERSON1,
  PERSON_ID: PERSON_ID3,
  'first-name': 'Mike',
  'last-name': 'Michelson'
}

PERSON3_RESULT = {
  **PERSON1_RESULT,
  **PERSON3
}

MEMBERSHIP1_RESULT = {
  'member_type': 'memberme',
  'member_id': '12345'
}

MEMBERSHIP1 = {
  **MEMBERSHIP1_RESULT,
  PERSON_ID: PERSON_ID1,
}

def version_id(manuscript_no, version_no):
  return '{}-{}'.format(manuscript_no, version_no)

MANUSCRIPT_ID1 = '12345'
MANUSCRIPT_VERSION_ID1 = version_id(MANUSCRIPT_ID1, 1)
MANUSCRIPT_TITLE1 = 'Manuscript Title1'

MANUSCRIPT_ID2 = '22222'
MANUSCRIPT_VERSION_ID2 = version_id(MANUSCRIPT_ID2, 2)
MANUSCRIPT_TITLE2 = 'Manuscript Title2'

MANUSCRIPT_ID3 = '33333'
MANUSCRIPT_VERSION_ID3 = version_id(MANUSCRIPT_ID3, 3)
MANUSCRIPT_TITLE3 = 'Manuscript Title3'

MANUSCRIPT_ID_FIELDS1 = {
  MANUSCRIPT_ID: MANUSCRIPT_ID1,
  VERSION_ID: MANUSCRIPT_VERSION_ID1
}

MANUSCRIPT_ID_FIELDS2 = {
  MANUSCRIPT_ID: MANUSCRIPT_ID2,
  VERSION_ID: MANUSCRIPT_VERSION_ID2
}

MANUSCRIPT_ID_FIELDS3 = {
  MANUSCRIPT_ID: MANUSCRIPT_ID3,
  VERSION_ID: MANUSCRIPT_VERSION_ID3
}

create_manuscript_id_fields = lambda i: ({
  MANUSCRIPT_ID: str(i),
  VERSION_ID: version_id(str(i), 1)
})

MANUSCRIPT_ID_FIELDS4 = create_manuscript_id_fields(4)
MANUSCRIPT_ID_FIELDS5 = create_manuscript_id_fields(5)

DECISSION_ACCEPTED = 'Accept Full Submission'
DECISSION_REJECTED = 'Reject Full Submission'

TYPE_RESEARCH_ARTICLE = 'Research Article'

MANUSCRIPT_VERSION1_RESULT = {
  **MANUSCRIPT_ID_FIELDS1,
  MANUSCRIPT_ID: MANUSCRIPT_ID1,
  'authors': [],
  'senior_editors': [],
  'doi': None,
  'title': MANUSCRIPT_TITLE1,
  'decision': DECISSION_ACCEPTED,
  'manuscript_type': TYPE_RESEARCH_ARTICLE,
  'subject_areas': []
}

MANUSCRIPT_VERSION1 = MANUSCRIPT_VERSION1_RESULT

MANUSCRIPT_VERSION2_RESULT = {
  **MANUSCRIPT_VERSION1_RESULT,
  **MANUSCRIPT_ID_FIELDS2,
  'title': MANUSCRIPT_TITLE2
}

MANUSCRIPT_VERSION2 = MANUSCRIPT_VERSION2_RESULT

MANUSCRIPT_VERSION3_RESULT = {
  **MANUSCRIPT_VERSION1_RESULT,
  **MANUSCRIPT_ID_FIELDS3,
  'title': MANUSCRIPT_TITLE3
}

MANUSCRIPT_VERSION3 = MANUSCRIPT_VERSION3_RESULT

MANUSCRIPT_VERSION4_RESULT = {
  **MANUSCRIPT_VERSION1_RESULT,
  **MANUSCRIPT_ID_FIELDS4
}

MANUSCRIPT_VERSION4 = MANUSCRIPT_VERSION4_RESULT

MANUSCRIPT_VERSION5_RESULT = {
  **MANUSCRIPT_VERSION1_RESULT,
  **MANUSCRIPT_ID_FIELDS5
}

MANUSCRIPT_VERSION5 = MANUSCRIPT_VERSION5_RESULT

KEYWORD1 = 'keyword1'

MANUSCRIPT_KEYWORD1 = {
  **MANUSCRIPT_ID_FIELDS1,
  'keyword': KEYWORD1
}

SUBJECT_AREA1 = 'Subject Area 1'
SUBJECT_AREA2 = 'Subject Area 2'

MANUSCRIPT_SUBJECT_AREA1 = {
  **MANUSCRIPT_ID_FIELDS1,
  'subject_area': SUBJECT_AREA1
}

MANUSCRIPT_SUBJECT_AREA2 = {
  **MANUSCRIPT_ID_FIELDS1,
  'subject_area': SUBJECT_AREA2
}

DOCVEC1 = [1, 1]
DOCVEC2 = [2, 2]

ABSTRACT_DOCVEC1 = {
  **MANUSCRIPT_ID_FIELDS1,
  LDA_DOCVEC_COLUMN: DOCVEC1
}

ABSTRACT_DOCVEC2 = {
  **MANUSCRIPT_ID_FIELDS2,
  LDA_DOCVEC_COLUMN: DOCVEC2
}

DOI1 = 'doi/1'

AUTHOR1 = {
  **MANUSCRIPT_ID_FIELDS1,
  PERSON_ID: PERSON_ID1
}

AUTHOR2 = {
  **MANUSCRIPT_ID_FIELDS1,
  PERSON_ID: PERSON_ID2
}

AUTHOR3 = {
  **MANUSCRIPT_ID_FIELDS1,
  PERSON_ID: PERSON_ID3
}

STAGE_CONTACTING_REVIEWERS = 'Contacting Reviewers'
STAGE_REVIEW_ACCEPTED = 'Reviewers Accept'
STAGE_REVIEW_DECLINE = 'Reviewers Decline'
STAGE_REVIEW_COMPLETE = 'Review Received'

MANUSCRIPT_HISTORY_REVIEW_COMPLETE1 = {
  **MANUSCRIPT_ID_FIELDS1,
  'stage_name': STAGE_REVIEW_COMPLETE,
  'stage_timestamp': pd.Timestamp('2017-01-01'),
  PERSON_ID: PERSON_ID1
}

POTENTIAL_REVIEWER1 = {
  'person': PERSON1_RESULT,
  'scores': {
    'combined': 1.0,
    'keyword': 1.0,
    'similarity': None,
    'by_manuscript': [{
      **MANUSCRIPT_ID_FIELDS1,
      'combined': 1.0,
      'keyword': 1.0,
      'similarity': None
    }]
  }
}

POTENTIAL_REVIEWER2 = {
  **POTENTIAL_REVIEWER1,
  'person': PERSON2_RESULT
}

KEYWORD_SEARCH1 = {
  'keywords': [KEYWORD1]
}

PP = pprint.PrettyPrinter(indent=2, width=40)

def create_recommend_reviewers(datasets):
  engine = sqlalchemy.create_engine('sqlite://', echo=False)
  logger.debug("engine driver: %s", engine.driver)
  db = database.Database(engine)
  db.update_schema()

  sorted_table_names = db.sorted_table_names()

  unknown_table_names = set(datasets.keys()) - set(sorted_table_names)
  if len(unknown_table_names) > 0:
    raise Exception("unknown table names: {}".format(unknown_table_names))

  for table_name in sorted_table_names:
    if table_name in datasets:
      logger.debug("datasets %s:\n%s", table_name, datasets[table_name])
      objs = [{
        k: v if not isinstance(v, list) and not pd.isnull(v) else None
        for k, v in row.items()
      } for row in datasets[table_name].to_dict(orient='records')]
      logger.debug("objs %s:\n%s", table_name, objs)
      db[table_name].create_list(objs)

  logger.debug("view manuscript_person_review_times:\n%s",
    db.manuscript_person_review_times.read_frame())
  logger.debug("view person_review_stats_overall:\n%s",
    db.person_review_stats_overall.read_frame())

  manuscript_model = ManuscriptModel(db)
  similarity_model = DocumentSimilarityModel(
    db,
    manuscript_model=manuscript_model
  )
  return RecommendReviewers(
    db, manuscript_model=manuscript_model, similarity_model=similarity_model
  )

def test_no_match():
  recommend_reviewers = create_recommend_reviewers(DATASETS)
  result = recommend_reviewers.recommend(keywords='', manuscript_no='')
  assert result['matching_manuscripts'] == []

def test_matching_manuscript():
  datasets = dict(DATASETS)
  datasets['person'] = pd.DataFrame([
    PERSON1
  ], columns=PERSON.columns)
  datasets['manuscript_version'] = pd.DataFrame([
    MANUSCRIPT_VERSION1
  ], columns=MANUSCRIPT_VERSION.columns)
  datasets['manuscript_keyword'] = pd.DataFrame([
    MANUSCRIPT_KEYWORD1
  ], columns=MANUSCRIPT_KEYWORD.columns)
  recommend_reviewers = create_recommend_reviewers(datasets)
  result = recommend_reviewers.recommend(keywords='', manuscript_no=MANUSCRIPT_ID1)
  assert result == {
    'potential_reviewers': [],
    'matching_manuscripts': [{
      **MANUSCRIPT_VERSION1_RESULT
    }]
  }

def test_matching_manuscript_should_include_subject_areas():
  datasets = dict(DATASETS)
  datasets['person'] = pd.DataFrame([
    PERSON1
  ], columns=PERSON.columns)
  datasets['manuscript_version'] = pd.DataFrame([
    MANUSCRIPT_VERSION1
  ], columns=MANUSCRIPT_VERSION.columns)
  datasets['manuscript_keyword'] = pd.DataFrame([
    MANUSCRIPT_KEYWORD1
  ], columns=MANUSCRIPT_KEYWORD.columns)
  datasets[SUBJECT_AREAS_DATASET] = pd.DataFrame([
    MANUSCRIPT_SUBJECT_AREA1,
    MANUSCRIPT_SUBJECT_AREA2
  ], columns=MANUSCRIPT_SUBJECT_AREAS.columns)
  recommend_reviewers = create_recommend_reviewers(datasets)
  result = recommend_reviewers.recommend(keywords='', manuscript_no=MANUSCRIPT_ID1)
  subject_areas = result['matching_manuscripts'][0]['subject_areas']
  assert subject_areas == [SUBJECT_AREA1, SUBJECT_AREA2]


def test_matching_manuscript_with_docvecs():
  datasets = dict(DATASETS)
  datasets['person'] = pd.DataFrame([
    PERSON1
  ], columns=PERSON.columns)
  datasets['manuscript_version'] = pd.DataFrame([
    MANUSCRIPT_VERSION1
  ], columns=MANUSCRIPT_VERSION.columns)
  datasets['manuscript_keyword'] = pd.DataFrame([
    MANUSCRIPT_KEYWORD1
  ], columns=MANUSCRIPT_KEYWORD.columns)
  datasets[ML_MANUSCRIPT_DATA_DATASET] = pd.DataFrame([
    ABSTRACT_DOCVEC1
  ], columns=ML_MANUSCRIPT_DATA.columns)
  recommend_reviewers = create_recommend_reviewers(datasets)
  recommend_reviewers.recommend(keywords='', manuscript_no=MANUSCRIPT_ID1)


def test_matching_manuscript_with_none_docvecs():
  datasets = dict(DATASETS)
  datasets['person'] = pd.DataFrame([
    PERSON1
  ], columns=PERSON.columns)
  datasets['manuscript_version'] = pd.DataFrame([
    MANUSCRIPT_VERSION1
  ], columns=MANUSCRIPT_VERSION.columns)
  datasets['manuscript_keyword'] = pd.DataFrame([
    MANUSCRIPT_KEYWORD1
  ], columns=MANUSCRIPT_KEYWORD.columns)
  datasets[ML_MANUSCRIPT_DATA_DATASET] = pd.DataFrame([
    ABSTRACT_DOCVEC1,
    {
      **ABSTRACT_DOCVEC2,
      LDA_DOCVEC_COLUMN: None
    }
  ], columns=ML_MANUSCRIPT_DATA.columns)
  recommend_reviewers = create_recommend_reviewers(datasets)
  recommend_reviewers.recommend(keywords='', manuscript_no=MANUSCRIPT_ID1)


def test_matching_manuscript_should_recommend_early_career_reviewer_by_subject_area():
  datasets = dict(DATASETS)
  datasets['person'] = pd.DataFrame([{
    **PERSON1,
    'is_early_career_researcher': True
  }], columns=PERSON.columns)
  datasets['person_subject_area'] = pd.DataFrame([{
    'person_id': PERSON_ID1,
    'subject_area': SUBJECT_AREA1
  }], columns=PERSON_SUBJECT_AREA.columns)
  recommend_reviewers = create_recommend_reviewers(datasets)
  result = recommend_reviewers.recommend(
    subject_area=SUBJECT_AREA1, keywords=None, manuscript_no=None
  )
  logger.debug("result: %s", PP.pformat(result))
  recommended_person_ids = [
    (r['person'][PERSON_ID], r['person'].get('is_early_career_researcher'))
    for r in result['potential_reviewers']
  ]
  assert recommended_person_ids == [(PERSON_ID1, True)]

def test_matching_manuscript_should_return_draft_version_with_authors():
  datasets = dict(DATASETS)
  datasets['person'] = pd.DataFrame([
    PERSON1
  ], columns=PERSON.columns)
  datasets['manuscript_version'] = pd.DataFrame([{
    **MANUSCRIPT_VERSION1,
    'decision': DECISSION_REJECTED
  }], columns=MANUSCRIPT_VERSION.columns)
  datasets['manuscript_author'] = pd.DataFrame([
    AUTHOR1
  ], columns=MANUSCRIPT_AUTHOR.columns)
  datasets['manuscript_keyword'] = pd.DataFrame([
    MANUSCRIPT_KEYWORD1
  ], columns=MANUSCRIPT_KEYWORD.columns)
  recommend_reviewers = create_recommend_reviewers(datasets)
  result = recommend_reviewers.recommend(keywords='', manuscript_no=MANUSCRIPT_ID1)
  logger.debug("result: %s", PP.pformat(result))
  assert [m[MANUSCRIPT_ID] for m in result['matching_manuscripts']] == [MANUSCRIPT_ID1]
  assert [p[PERSON_ID] for p in result['matching_manuscripts'][0]['authors']] == [PERSON_ID1]

def test_matching_manuscript_should_return_multiple_authors():
  datasets = dict(DATASETS)
  datasets['person'] = pd.DataFrame([
    PERSON1,
    PERSON2
  ], columns=PERSON.columns)
  datasets['manuscript_version'] = pd.DataFrame([
    MANUSCRIPT_VERSION1,
    MANUSCRIPT_VERSION2
  ], columns=MANUSCRIPT_VERSION.columns)
  datasets['manuscript_author'] = pd.DataFrame([
    AUTHOR1,
    {
      **AUTHOR1,
      **MANUSCRIPT_ID_FIELDS2
    },
    {
      **AUTHOR2,
      **MANUSCRIPT_ID_FIELDS1
    }
  ], columns=MANUSCRIPT_AUTHOR.columns)
  recommend_reviewers = create_recommend_reviewers(datasets)
  result = recommend_reviewers.recommend(keywords='', manuscript_no=MANUSCRIPT_ID1)
  logger.debug("result: %s", PP.pformat(result))
  author_person_ids = [p[PERSON_ID] for p in result['matching_manuscripts'][0]['authors']]
  assert set(author_person_ids) == set([PERSON_ID1, PERSON_ID2])

def test_matching_manuscript_should_not_recommend_its_authors():
  datasets = dict(DATASETS)
  datasets['person'] = pd.DataFrame([
    PERSON1,
    PERSON2
  ], columns=PERSON.columns)
  datasets['manuscript_version'] = pd.DataFrame([
    MANUSCRIPT_VERSION1,
    MANUSCRIPT_VERSION2
  ], columns=MANUSCRIPT_VERSION.columns)
  datasets['manuscript_keyword'] = pd.DataFrame([
    MANUSCRIPT_KEYWORD1,
    {
      **MANUSCRIPT_KEYWORD1,
      **MANUSCRIPT_ID_FIELDS2
    }
  ], columns=MANUSCRIPT_KEYWORD.columns)
  datasets['manuscript_author'] = pd.DataFrame([
    AUTHOR1,
    {
      **AUTHOR1,
      **MANUSCRIPT_ID_FIELDS2
    },
    {
      **AUTHOR2,
      **MANUSCRIPT_ID_FIELDS2
    }
  ], columns=MANUSCRIPT_AUTHOR.columns)
  recommend_reviewers = create_recommend_reviewers(datasets)
  result = recommend_reviewers.recommend(keywords='', manuscript_no=MANUSCRIPT_ID1)
  logger.debug("result: %s", PP.pformat(result))
  recommended_person_ids = [r['person'][PERSON_ID] for r in result['potential_reviewers']]
  assert recommended_person_ids == [PERSON_ID2]

def test_matching_manuscript_should_only_recommend_authors_of_matching_subject_areas():
  datasets = dict(DATASETS)
  datasets['person'] = pd.DataFrame([
    PERSON1,
    PERSON2,
    PERSON3
  ], columns=PERSON.columns)
  datasets['manuscript_version'] = pd.DataFrame([
    MANUSCRIPT_VERSION1,
    MANUSCRIPT_VERSION2,
    MANUSCRIPT_VERSION3
  ], columns=MANUSCRIPT_VERSION.columns)
  datasets['manuscript_keyword'] = pd.DataFrame([
    MANUSCRIPT_KEYWORD1,
    {
      **MANUSCRIPT_KEYWORD1,
      **MANUSCRIPT_ID_FIELDS2
    },
    {
      **MANUSCRIPT_KEYWORD1,
      **MANUSCRIPT_ID_FIELDS3
    }
  ], columns=MANUSCRIPT_KEYWORD.columns)
  datasets[SUBJECT_AREAS_DATASET] = pd.DataFrame([
    MANUSCRIPT_SUBJECT_AREA1,
    {
      **MANUSCRIPT_SUBJECT_AREA2,
      **MANUSCRIPT_ID_FIELDS2
    },
    {
      **MANUSCRIPT_SUBJECT_AREA1,
      **MANUSCRIPT_ID_FIELDS3
    }
  ], columns=MANUSCRIPT_SUBJECT_AREAS.columns)
  datasets['manuscript_author'] = pd.DataFrame([
    AUTHOR1,
    {
      **AUTHOR2,
      **MANUSCRIPT_ID_FIELDS2
    },
    {
      **AUTHOR3,
      **MANUSCRIPT_ID_FIELDS3
    }
  ], columns=MANUSCRIPT_AUTHOR.columns)
  recommend_reviewers = create_recommend_reviewers(datasets)
  result = recommend_reviewers.recommend(keywords='', manuscript_no=MANUSCRIPT_ID1)
  logger.debug("result: %s", PP.pformat(result))
  recommended_person_ids = [r['person'][PERSON_ID] for r in result['potential_reviewers']]
  assert recommended_person_ids == [PERSON_ID3]


def test_matching_one_keyword_author_should_return_author():
  datasets = dict(DATASETS)
  datasets['person'] = pd.DataFrame([
    PERSON1
  ], columns=PERSON.columns)
  datasets['manuscript_version'] = pd.DataFrame([
    MANUSCRIPT_VERSION1
  ], columns=MANUSCRIPT_VERSION.columns)
  datasets['manuscript_author'] = pd.DataFrame([
    AUTHOR1
  ], columns=MANUSCRIPT_AUTHOR.columns)
  datasets['manuscript_keyword'] = pd.DataFrame([
    MANUSCRIPT_KEYWORD1
  ], columns=MANUSCRIPT_KEYWORD.columns)
  recommend_reviewers = create_recommend_reviewers(datasets)
  result = recommend_reviewers.recommend(keywords=KEYWORD1, manuscript_no='')
  logger.debug("result: %s", PP.pformat(result))
  assert [r['person'][PERSON_ID] for r in result['potential_reviewers']] == [PERSON_ID1]

def test_matching_one_keyword_author_should_not_return_author_of_rejected_manuscripts():
  datasets = dict(DATASETS)
  datasets['person'] = pd.DataFrame([
    PERSON1
  ], columns=PERSON.columns)
  datasets['manuscript_version'] = pd.DataFrame([{
    **MANUSCRIPT_VERSION1,
    'decision': DECISSION_REJECTED
  }], columns=MANUSCRIPT_VERSION.columns)
  datasets['manuscript_author'] = pd.DataFrame([
    AUTHOR1
  ], columns=MANUSCRIPT_AUTHOR.columns)
  datasets['manuscript_keyword'] = pd.DataFrame([
    MANUSCRIPT_KEYWORD1
  ], columns=MANUSCRIPT_KEYWORD.columns)
  recommend_reviewers = create_recommend_reviewers(datasets)
  result = recommend_reviewers.recommend(keywords=KEYWORD1, manuscript_no='')
  logger.debug("result: %s", PP.pformat(result))
  assert result['potential_reviewers'] == []

def _review_complete_stages(id_fields, contacted, accepted, reviewed):
  return [{
    **id_fields,
    'stage_name': STAGE_CONTACTING_REVIEWERS,
    'stage_timestamp': contacted
  }, {
    **id_fields,
    'stage_name': STAGE_REVIEW_ACCEPTED,
    'stage_timestamp': accepted
  }, {
    **id_fields,
    'stage_name': STAGE_REVIEW_COMPLETE,
    'stage_timestamp': reviewed
  }]

def _declined_stages(id_fields, contacted, declined):
  return [{
    **id_fields,
    'stage_name': STAGE_CONTACTING_REVIEWERS,
    'stage_timestamp': contacted
  }, {
    **id_fields,
    'stage_name': STAGE_REVIEW_DECLINE,
    'stage_timestamp': declined
  }]

def _awaiting_accept_stages(id_fields, contacted):
  return [{
    **id_fields,
    'stage_name': STAGE_CONTACTING_REVIEWERS,
    'stage_timestamp': contacted
  }]

def _awaiting_review_stages(id_fields, contacted, accepted):
  return [{
    **id_fields,
    'stage_name': STAGE_CONTACTING_REVIEWERS,
    'stage_timestamp': contacted
  }, {
    **id_fields,
    'stage_name': STAGE_REVIEW_ACCEPTED,
    'stage_timestamp': accepted
  }]

def test_matching_one_keyword_author_should_return_stats():
  datasets = dict(DATASETS)
  datasets['person'] = pd.DataFrame([
    PERSON1
  ], columns=PERSON.columns)
  datasets['manuscript_version'] = pd.DataFrame([
    MANUSCRIPT_VERSION1,
    MANUSCRIPT_VERSION2,
    MANUSCRIPT_VERSION3,
    MANUSCRIPT_VERSION4,
    MANUSCRIPT_VERSION5
  ], columns=MANUSCRIPT_VERSION.columns)
  datasets['manuscript_author'] = pd.DataFrame([
    AUTHOR1
  ], columns=MANUSCRIPT_AUTHOR.columns)
  datasets['manuscript_keyword'] = pd.DataFrame([
    MANUSCRIPT_KEYWORD1
  ], columns=MANUSCRIPT_KEYWORD.columns)
  # add two review durations (two stages each)
  # also add an open review (accepted)
  datasets['manuscript_stage'] = pd.DataFrame(
    (
      _review_complete_stages(
        {
          **MANUSCRIPT_ID_FIELDS1,
          PERSON_ID: PERSON_ID1
        },
        contacted=pd.Timestamp('2017-01-01'),
        accepted=pd.Timestamp('2017-01-02'),
        reviewed=pd.Timestamp('2017-01-03')
      ) +
      _review_complete_stages(
        {
          **MANUSCRIPT_ID_FIELDS2,
          PERSON_ID: PERSON_ID1
        },
        contacted=pd.Timestamp('2017-02-01'),
        accepted=pd.Timestamp('2017-02-02'),
        reviewed=pd.Timestamp('2017-02-04')
      ) +
      _awaiting_accept_stages(
        {
          **MANUSCRIPT_ID_FIELDS3,
          PERSON_ID: PERSON_ID1
        },
        contacted=pd.Timestamp('2017-02-01')
      ) +
      _awaiting_review_stages(
        {
          **MANUSCRIPT_ID_FIELDS4,
          PERSON_ID: PERSON_ID1
        },
        contacted=pd.Timestamp('2017-02-01'),
        accepted=pd.Timestamp('2017-02-02')
      ) +
      _declined_stages(
        {
          **MANUSCRIPT_ID_FIELDS5,
          PERSON_ID: PERSON_ID1
        },
        contacted=pd.Timestamp('2017-02-01'),
        declined=pd.Timestamp('2017-02-02')
      )
    ), columns=MANUSCRIPT_STAGE.columns
  )
  recommend_reviewers = create_recommend_reviewers(datasets)
  review_duration = {
    'min': 1.0,
    'mean': 1.5,
    'max': 2,
    'count': 2
  }
  overall_stats = {
    'review_duration': review_duration,
    'reviews_in_progress': 1,
    'waiting_to_be_accepted': 1,
    'declined': 1
  }
  result = recommend_reviewers.recommend(keywords=KEYWORD1, manuscript_no='')
  result_person = result['potential_reviewers'][0]['person']
  logger.debug("result_person: %s", PP.pformat(result_person))
  assert result_person['stats'] == {
    'overall': overall_stats,
    'last_12m': overall_stats
  }

def test_matching_one_keyword_author_should_return_memberships():
  datasets = dict(DATASETS)
  datasets['person'] = pd.DataFrame([
    PERSON1
  ], columns=PERSON.columns)
  datasets['person_membership'] = pd.DataFrame([
    MEMBERSHIP1,
  ], columns=PERSON_MEMBERSHIP.columns)
  datasets['manuscript_version'] = pd.DataFrame([
    MANUSCRIPT_VERSION1
  ], columns=MANUSCRIPT_VERSION.columns)
  datasets['manuscript_author'] = pd.DataFrame([
    AUTHOR1
  ], columns=MANUSCRIPT_AUTHOR.columns)
  datasets['manuscript_keyword'] = pd.DataFrame([
    MANUSCRIPT_KEYWORD1
  ], columns=MANUSCRIPT_KEYWORD.columns)
  recommend_reviewers = create_recommend_reviewers(datasets)
  result = recommend_reviewers.recommend(keywords=KEYWORD1, manuscript_no='')
  result_person = result['potential_reviewers'][0]['person']
  logger.debug("result_person: %s", PP.pformat(result_person))
  assert result_person.get('memberships') == [MEMBERSHIP1_RESULT]

def test_matching_one_keyword_author_should_return_other_accepted_papers():
  datasets = dict(DATASETS)
  datasets['person'] = pd.DataFrame([
    PERSON1
  ], columns=PERSON.columns)
  datasets['manuscript_version'] = pd.DataFrame([
    MANUSCRIPT_VERSION1, {
      **MANUSCRIPT_VERSION2,
      'decision': DECISSION_ACCEPTED
    }
  ], columns=MANUSCRIPT_VERSION.columns)
  datasets['manuscript_author'] = pd.DataFrame([
    AUTHOR1, {
      **AUTHOR1,
      **MANUSCRIPT_ID_FIELDS2
    }
  ], columns=MANUSCRIPT_AUTHOR.columns)
  datasets['manuscript_keyword'] = pd.DataFrame([
    MANUSCRIPT_KEYWORD1
  ], columns=MANUSCRIPT_KEYWORD.columns)
  recommend_reviewers = create_recommend_reviewers(datasets)
  result = recommend_reviewers.recommend(keywords=KEYWORD1, manuscript_no='')
  author_of_manuscripts = result['potential_reviewers'][0]['author_of_manuscripts']
  author_of_manuscript_ids = [m[MANUSCRIPT_ID] for m in author_of_manuscripts]
  logger.debug("author_of_manuscripts: %s", PP.pformat(author_of_manuscripts))
  logger.debug("author_of_manuscript_ids: %s", author_of_manuscript_ids)
  assert set(author_of_manuscript_ids) == set([
    MANUSCRIPT_VERSION1_RESULT[MANUSCRIPT_ID],
    MANUSCRIPT_VERSION2_RESULT[MANUSCRIPT_ID]
  ])

def test_matching_one_keyword_author_should_not_return_other_draft_papers():
  datasets = dict(DATASETS)
  datasets['person'] = pd.DataFrame([
    PERSON1
  ], columns=PERSON.columns)
  datasets['manuscript_version'] = pd.DataFrame([
    MANUSCRIPT_VERSION1, {
      **MANUSCRIPT_VERSION2,
      'decision': DECISSION_REJECTED
    }
  ], columns=MANUSCRIPT_VERSION.columns)
  datasets['manuscript_author'] = pd.DataFrame([
    AUTHOR1, {
      **AUTHOR1,
      **MANUSCRIPT_ID_FIELDS2
    }
  ], columns=MANUSCRIPT_AUTHOR.columns)
  datasets['manuscript_keyword'] = pd.DataFrame([
    MANUSCRIPT_KEYWORD1
  ], columns=MANUSCRIPT_KEYWORD.columns)
  recommend_reviewers = create_recommend_reviewers(datasets)
  result = recommend_reviewers.recommend(keywords=KEYWORD1, manuscript_no='')
  logger.debug("result: %s", result)
  assert (
    [m[MANUSCRIPT_ID] for m in result['potential_reviewers'][0]['author_of_manuscripts']] ==
    [MANUSCRIPT_ID1]
  )


def test_matching_one_keyword_should_return_previous_reviewer():
  datasets = dict(DATASETS)
  datasets['person'] = pd.DataFrame([
    PERSON1
  ], columns=PERSON.columns)
  datasets['manuscript_version'] = pd.DataFrame([
    MANUSCRIPT_VERSION1
  ], columns=MANUSCRIPT_VERSION.columns)
  datasets['manuscript_stage'] = pd.DataFrame([
    MANUSCRIPT_HISTORY_REVIEW_COMPLETE1
  ], columns=MANUSCRIPT_STAGE.columns)
  datasets['manuscript_keyword'] = pd.DataFrame([
    MANUSCRIPT_KEYWORD1
  ], columns=MANUSCRIPT_KEYWORD.columns)
  recommend_reviewers = create_recommend_reviewers(datasets)
  result = recommend_reviewers.recommend(keywords=KEYWORD1, manuscript_no='')
  logger.debug("result: %s", PP.pformat(result))
  assert [r['person'][PERSON_ID] for r in result['potential_reviewers']] == [PERSON_ID1]
  # Note: reviewer_of_manuscripts no longer returned
  # assert ([
  #   m[MANUSCRIPT_ID]
  #   for m in result['potential_reviewers'][0]['reviewer_of_manuscripts']
  # ] == [MANUSCRIPT_ID1])
  # Note: reviewers are no longer returned
  # assert ([
  #   p[PERSON_ID]
  #   for p in result['potential_reviewers'][0]['reviewer_of_manuscripts'][0]['reviewers']
  # ] == [PERSON_ID1])

def test_matching_one_keyword_previous_reviewer_should_return_reviewer_only_once():
  datasets = dict(DATASETS)
  datasets['person'] = pd.DataFrame([
    PERSON1
  ], columns=PERSON.columns)
  datasets['manuscript_version'] = pd.DataFrame([
    MANUSCRIPT_VERSION1
  ], columns=MANUSCRIPT_VERSION.columns)
  datasets['manuscript_stage'] = pd.DataFrame([
    {
      **MANUSCRIPT_HISTORY_REVIEW_COMPLETE1,
      'stage_timestamp': pd.Timestamp('2017-01-01'),
    },
    {
      **MANUSCRIPT_HISTORY_REVIEW_COMPLETE1,
      'stage_timestamp': pd.Timestamp('2017-01-02'),
    }
  ], columns=MANUSCRIPT_STAGE.columns)
  datasets['manuscript_keyword'] = pd.DataFrame([
    MANUSCRIPT_KEYWORD1
  ], columns=MANUSCRIPT_KEYWORD.columns)
  recommend_reviewers = create_recommend_reviewers(datasets)
  result = recommend_reviewers.recommend(keywords=KEYWORD1, manuscript_no='')
  logger.debug("result: %s", PP.pformat(result))
  assert\
    [
      r['person'][PERSON_ID]
      for r in result['potential_reviewers']
    ] == [PERSON_ID1]
  # Note: reviewers are no longer returned
  # assert\
  #   [
  #     r[PERSON_ID]
  #     for r in result['potential_reviewers'][0]\
  #       ['reviewer_of_manuscripts'][0]['reviewers']
  #   ] == [PERSON_ID1]
