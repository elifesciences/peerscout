import pprint
import logging
from contextlib import contextmanager

import pytest
import pandas as pd

from ...shared.database import populated_in_memory_database

from .ManuscriptModel import ManuscriptModel
from .DocumentSimilarityModel import DocumentSimilarityModel
from .manuscript_person_relationship_service import RelationshipTypes
from .RecommendReviewers import RecommendReviewers, set_debugv_enabled

from .test_data import (
  PERSON_ID,
  PERSON_ID1, PERSON_ID2, PERSON_ID3,
  PERSON1, PERSON2, PERSON3,
  MANUSCRIPT_VERSION1,
  MANUSCRIPT_ID1, MANUSCRIPT_ID2,
  MANUSCRIPT_ID_FIELDS1, MANUSCRIPT_ID_FIELDS2, MANUSCRIPT_ID_FIELDS3,
  MANUSCRIPT_ID_FIELDS4, MANUSCRIPT_ID_FIELDS5,
  MANUSCRIPT_TITLE1, MANUSCRIPT_TITLE2, MANUSCRIPT_TITLE3,
  MANUSCRIPT_KEYWORD1,
  MANUSCRIPT_ABSTRACT1,
  VALID_DECISIONS, VALID_MANUSCRIPT_TYPES,
  PUBLISHED_DECISIONS, PUBLISHED_MANUSCRIPT_TYPES,
  DECISSION_ACCEPTED, DECISSION_REJECTED,
  KEYWORD1
)

MANUSCRIPT_ID = 'manuscript_id'
VERSION_ID = 'version_id'

PERSON_ID = 'person_id'

MANUSCRIPT_ID_COLUMNS = [VERSION_ID]
PERSON_ID_COLUMNS = [PERSON_ID]

LDA_DOCVEC_COLUMN = 'lda_docvec'

EMAIL_1 = 'email1'
ROLE_1 = 'role1'

PERSON1_RESULT = {
  **PERSON1,
  'memberships': [],
  'dates_not_available': [],
  'stats': {
    'overall': None,
    'last_12m': None
  }
}

PERSON2_RESULT = {
  **PERSON1_RESULT,
  **PERSON2
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

MANUSCRIPT_VERSION1_RESULT = {
  **MANUSCRIPT_VERSION1,
  'authors': [],
  'senior_editors': [],
  'subject_areas': []
}

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
  PERSON_ID: PERSON_ID1,
  'seq': 0,
  'is_corresponding_author': False
}

AUTHOR2 = {
  **AUTHOR1,
  **MANUSCRIPT_ID_FIELDS1,
  PERSON_ID: PERSON_ID2
}

AUTHOR3 = {
  **AUTHOR1,
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

EARLY_CAREER_RESEARCHER_WITH_SUBJECT_AREAS_DATASET = {
  'person' : [{
    **PERSON1,
    'is_early_career_researcher': True
  }, {
    **PERSON2,
    'is_early_career_researcher': True
  }],
  'person_subject_area': [{
    'person_id': PERSON_ID1,
    'subject_area': SUBJECT_AREA1
  }, {
    'person_id': PERSON_ID2,
    'subject_area': SUBJECT_AREA2
  }]
}

class PersonRoles:
  SENIOR_EDITOR = 'Senior Editor'
  OTHER = 'Other'

PP = pprint.PrettyPrinter(indent=2, width=40)

def setup_module():
  logging.basicConfig(level=logging.DEBUG)
  set_debugv_enabled(True)
  logging.getLogger().setLevel(logging.DEBUG)

@pytest.fixture(name='logger')
def get_logger():
  return logging.getLogger('test')

@contextmanager
def create_recommend_reviewers(dataset, filter_by_subject_area_enabled=False):
  logger = get_logger()
  with populated_in_memory_database(dataset) as db:
    logger.debug("view manuscript_person_review_times:\n%s",
      db.manuscript_person_review_times.read_frame())
    logger.debug("view person_review_stats_overall:\n%s",
      db.person_review_stats_overall.read_frame())

    manuscript_model = ManuscriptModel(
      db,
      valid_decisions=VALID_DECISIONS,
      valid_manuscript_types=VALID_MANUSCRIPT_TYPES,
      published_decisions=PUBLISHED_DECISIONS,
      published_manuscript_types=PUBLISHED_MANUSCRIPT_TYPES
    )
    similarity_model = DocumentSimilarityModel(
      db,
      manuscript_model=manuscript_model
    )
    yield RecommendReviewers(
      db, manuscript_model=manuscript_model, similarity_model=similarity_model,
      filter_by_subject_area_enabled=filter_by_subject_area_enabled
    )

def recommend_for_dataset(dataset, filter_by_subject_area_enabled=False, **kwargs):
  with create_recommend_reviewers(
    dataset,
    filter_by_subject_area_enabled=filter_by_subject_area_enabled) as recommend_reviewers:

    result = recommend_reviewers.recommend(**kwargs)
    get_logger().debug("result: %s", PP.pformat(result))
    return result

def _potential_reviewers_person_ids(potential_reviewers):
  return [r['person'][PERSON_ID] for r in potential_reviewers]

def _potential_reviewer_scores_by_person_id(potential_reviewers):
  return {r['person'][PERSON_ID]: r['scores']['keyword'] for r in potential_reviewers}

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

@pytest.mark.slow
class TestRecommendReviewers:
  class TestRecommendReviewersRegular:
    def test_no_match(self):
      dataset = {
        'person' : [PERSON1],
        'manuscript_version': [MANUSCRIPT_VERSION1],
        'manuscript_keyword': [MANUSCRIPT_KEYWORD1]
      }
      result = recommend_for_dataset(dataset, keywords='', manuscript_no='unknown')
      assert result['matching_manuscripts'] == []
      assert result['potential_reviewers'] == []

    def test_matching_manuscript(self):
      dataset = {
        'person' : [PERSON1],
        'manuscript_version': [MANUSCRIPT_VERSION1],
        'manuscript_keyword': [MANUSCRIPT_KEYWORD1]
      }
      result = recommend_for_dataset(dataset, keywords='', manuscript_no=MANUSCRIPT_ID1)
      assert result == {
        'potential_reviewers': [],
        'matching_manuscripts': [{
          **MANUSCRIPT_VERSION1_RESULT
        }]
      }

    def test_matching_manuscript_should_include_subject_areas(self):
      dataset = {
        'person' : [PERSON1],
        'manuscript_version': [MANUSCRIPT_VERSION1],
        'manuscript_keyword': [MANUSCRIPT_KEYWORD1],
        'manuscript_subject_area': [
          MANUSCRIPT_SUBJECT_AREA1,
          MANUSCRIPT_SUBJECT_AREA2
        ]
      }
      result = recommend_for_dataset(dataset, keywords='', manuscript_no=MANUSCRIPT_ID1)
      subject_areas = result['matching_manuscripts'][0]['subject_areas']
      assert subject_areas == [SUBJECT_AREA1, SUBJECT_AREA2]

    def test_should_not_fail_for_manuscript_with_docvecs(self):
      dataset = {
        'person' : [PERSON1],
        'manuscript_version': [MANUSCRIPT_VERSION1],
        'manuscript_keyword': [MANUSCRIPT_KEYWORD1],
        'ml_manuscript_data': [ABSTRACT_DOCVEC1]
      }
      recommend_for_dataset(dataset, keywords='', manuscript_no=MANUSCRIPT_ID1)

    def test_should_not_fail_for_manuscript_with_partial_docvecs(self):
      dataset = {
        'person' : [PERSON1],
        'manuscript_version': [MANUSCRIPT_VERSION1],
        'manuscript_keyword': [MANUSCRIPT_KEYWORD1],
        'ml_manuscript_data': [
          ABSTRACT_DOCVEC1, {
            **ABSTRACT_DOCVEC2,
            LDA_DOCVEC_COLUMN: None
          }
        ]
      }
      recommend_for_dataset(dataset, keywords='', manuscript_no=MANUSCRIPT_ID1)

    def test_search_should_filter_early_career_reviewer_by_subject_area(self):
      dataset = EARLY_CAREER_RESEARCHER_WITH_SUBJECT_AREAS_DATASET
      result = recommend_for_dataset(
        dataset,
        subject_area=SUBJECT_AREA1, keywords=None, manuscript_no=None
      )
      recommended_person_ids = [
        (r['person'][PERSON_ID], r['person'].get('is_early_career_researcher'))
        for r in result['potential_reviewers']
      ]
      assert recommended_person_ids == [(PERSON_ID1, True)]

    def test_search_should_not_filter_early_career_reviewer_by_subject_area_if_blank(self):
      dataset = EARLY_CAREER_RESEARCHER_WITH_SUBJECT_AREAS_DATASET
      result = recommend_for_dataset(
        dataset,
        subject_area=None, keywords=KEYWORD1, manuscript_no=None
      )
      recommended_person_ids = [
        (r['person'][PERSON_ID], r['person'].get('is_early_career_researcher'))
        for r in result['potential_reviewers']
      ]
      assert (
        set(recommended_person_ids) ==
        {(PERSON_ID1, True), (PERSON_ID2, True)}
      )

    def test_matching_manuscript_should_filter_early_career_reviewer_by_subject_area(self):
      dataset = {
        **EARLY_CAREER_RESEARCHER_WITH_SUBJECT_AREAS_DATASET,
        'person': (
          EARLY_CAREER_RESEARCHER_WITH_SUBJECT_AREAS_DATASET['person'] +
          [PERSON3]
        ),
        'manuscript_version': [MANUSCRIPT_VERSION1],
        'manuscript_author': [{**AUTHOR3, **MANUSCRIPT_ID_FIELDS1}],
        'manuscript_subject_area': [MANUSCRIPT_SUBJECT_AREA1]
      }
      result = recommend_for_dataset(
        dataset, filter_by_subject_area_enabled=False,
        subject_area=None, keywords=None, manuscript_no=MANUSCRIPT_ID1
      )
      recommended_person_ids = [
        (r['person'][PERSON_ID], r['person'].get('is_early_career_researcher'))
        for r in result['potential_reviewers']
      ]
      assert recommended_person_ids == [(PERSON_ID1, True)]

    def test_matching_manuscript_should_return_draft_version_with_authors(self):
      dataset = {
        'person': [PERSON1],
        'manuscript_version': [{
          **MANUSCRIPT_VERSION1,
          'decision': DECISSION_REJECTED
        }],
        'manuscript_author': [AUTHOR1],
        'manuscript_keyword': [MANUSCRIPT_KEYWORD1]
      }
      result = recommend_for_dataset(dataset, keywords='', manuscript_no=MANUSCRIPT_ID1)
      assert [m[MANUSCRIPT_ID] for m in result['matching_manuscripts']] == [MANUSCRIPT_ID1]
      assert [p[PERSON_ID] for p in result['matching_manuscripts'][0]['authors']] == [PERSON_ID1]

    def test_matching_manuscript_should_return_multiple_authors(self):
      dataset = {
        'person': [PERSON1, PERSON2],
        'manuscript_version': [MANUSCRIPT_VERSION1, MANUSCRIPT_VERSION2],
        'manuscript_author': [
          AUTHOR1,
          {**AUTHOR1, **MANUSCRIPT_ID_FIELDS2},
          {**AUTHOR2, **MANUSCRIPT_ID_FIELDS1}
        ]
      }
      result = recommend_for_dataset(dataset, keywords='', manuscript_no=MANUSCRIPT_ID1)
      author_person_ids = [p[PERSON_ID] for p in result['matching_manuscripts'][0]['authors']]
      assert set(author_person_ids) == set([PERSON_ID1, PERSON_ID2])

    def test_matching_manuscript_should_indicate_corresponding_authors(self):
      dataset = {
        'person': [PERSON1, PERSON2],
        'manuscript_version': [MANUSCRIPT_VERSION1, MANUSCRIPT_VERSION2],
        'manuscript_author': [
          {
            **AUTHOR1,
            'is_corresponding_author': True
          },
          {
            **AUTHOR2,
            **MANUSCRIPT_ID_FIELDS1,
            'is_corresponding_author': False
          },
          {
            # make author1 not the corresponding author of another manuscript
            **AUTHOR1,
            **MANUSCRIPT_ID_FIELDS2,
            'is_corresponding_author': False
          }
        ]
      }
      result = recommend_for_dataset(dataset, keywords='', manuscript_no=MANUSCRIPT_ID1)
      authors = sorted(result['matching_manuscripts'][0]['authors'], key=lambda p: p[PERSON_ID])
      author_summary = [(p[PERSON_ID], p.get('is_corresponding_author')) for p in authors]
      assert author_summary == [(PERSON_ID1, True), (PERSON_ID2, False)]

    def test_matching_manuscript_should_not_recommend_its_authors(self):
      dataset = {
        'person': [PERSON1, PERSON2],
        'manuscript_version': [MANUSCRIPT_VERSION1, MANUSCRIPT_VERSION2],
        'manuscript_keyword': [
          MANUSCRIPT_KEYWORD1,
          {**MANUSCRIPT_KEYWORD1, **MANUSCRIPT_ID_FIELDS2}
        ],
        'manuscript_author': [
          AUTHOR1,
          {**AUTHOR1, **MANUSCRIPT_ID_FIELDS2},
          {**AUTHOR2, **MANUSCRIPT_ID_FIELDS2}
        ]
      }
      result = recommend_for_dataset(dataset, keywords='', manuscript_no=MANUSCRIPT_ID1)
      recommended_person_ids = [r['person'][PERSON_ID] for r in result['potential_reviewers']]
      assert recommended_person_ids == [PERSON_ID2]

    def _do_test_matching_manuscript_should_filter_by_subject_areas_if_enabled(
      self, filter_by_subject_area_enabled):
      dataset = {
        'person': [PERSON1, PERSON2, PERSON3],
        'manuscript_version': [MANUSCRIPT_VERSION1, MANUSCRIPT_VERSION2, MANUSCRIPT_VERSION3],
        'manuscript_keyword': [
          MANUSCRIPT_KEYWORD1,
          {**MANUSCRIPT_KEYWORD1, **MANUSCRIPT_ID_FIELDS2},
          {**MANUSCRIPT_KEYWORD1, **MANUSCRIPT_ID_FIELDS3}
        ],
        'manuscript_subject_area': [
          MANUSCRIPT_SUBJECT_AREA1,
          {**MANUSCRIPT_SUBJECT_AREA2, **MANUSCRIPT_ID_FIELDS2},
          {**MANUSCRIPT_SUBJECT_AREA1, **MANUSCRIPT_ID_FIELDS3}
        ],
        'manuscript_author': [
          AUTHOR1,
          {**AUTHOR2, **MANUSCRIPT_ID_FIELDS2},
          {**AUTHOR3, **MANUSCRIPT_ID_FIELDS3}
        ]
      }
      result = recommend_for_dataset(
        dataset, filter_by_subject_area_enabled=filter_by_subject_area_enabled,
        keywords='', manuscript_no=MANUSCRIPT_ID1
      )
      recommended_person_ids = [r['person'][PERSON_ID] for r in result['potential_reviewers']]
      if filter_by_subject_area_enabled:
        assert recommended_person_ids == [PERSON_ID3]
      else:
        assert set(recommended_person_ids) == {PERSON_ID2, PERSON_ID3}

    def test_matching_manuscript_should_filter_by_subject_areas_if_enabled(self):
      self._do_test_matching_manuscript_should_filter_by_subject_areas_if_enabled(
        filter_by_subject_area_enabled=True
      )

    def test_matching_manuscript_should_not_filter_by_subject_areas_if_disabled(self):
      self._do_test_matching_manuscript_should_filter_by_subject_areas_if_enabled(
        filter_by_subject_area_enabled=False
      )

    def test_matching_manuscript_should_filter_by_search_subject_area_only(self):
      dataset = {
        'person': [PERSON2, PERSON3],
        'manuscript_version': [MANUSCRIPT_VERSION2, MANUSCRIPT_VERSION3],
        'manuscript_subject_area': [
          MANUSCRIPT_SUBJECT_AREA1,
          {
            **MANUSCRIPT_SUBJECT_AREA2,
            **MANUSCRIPT_ID_FIELDS2
          },
          {
            **MANUSCRIPT_SUBJECT_AREA1,
            **MANUSCRIPT_ID_FIELDS3
          }
        ],
        'manuscript_author': [
          {
            **AUTHOR2,
            **MANUSCRIPT_ID_FIELDS2
          },
          {
            **AUTHOR3,
            **MANUSCRIPT_ID_FIELDS3
          }
        ]
      }
      result = recommend_for_dataset(
        dataset, filter_by_subject_area_enabled=False,
        keywords='', subject_area=SUBJECT_AREA1
      )
      recommended_person_ids = [r['person'][PERSON_ID] for r in result['potential_reviewers']]
      assert recommended_person_ids == [PERSON_ID3]

    def test_matching_one_keyword_author_should_return_author(self):
      dataset = {
        'person': [PERSON1],
        'manuscript_version': [MANUSCRIPT_VERSION1],
        'manuscript_author': [AUTHOR1],
        'manuscript_keyword': [MANUSCRIPT_KEYWORD1]
      }
      result = recommend_for_dataset(dataset, keywords=KEYWORD1, manuscript_no='')
      assert [r['person'][PERSON_ID] for r in result['potential_reviewers']] == [PERSON_ID1]

    def test_matching_one_keyword_author_should_not_suggest_authors_of_rejected_manuscripts(self):
      dataset = {
        'person': [PERSON1],
        'manuscript_version': [{
          **MANUSCRIPT_VERSION1,
          'decision': DECISSION_REJECTED
        }],
        'manuscript_author': [AUTHOR1],
        'manuscript_keyword': [MANUSCRIPT_KEYWORD1]
      }
      result = recommend_for_dataset(dataset, keywords=KEYWORD1, manuscript_no='')
      assert result['potential_reviewers'] == []

    def test_matching_one_keyword_author_should_suggest_reviewers_of_rejected_manuscripts(self):
      dataset = {
        'person': [PERSON1],
        'manuscript_version': [{
          **MANUSCRIPT_VERSION1,
          'decision': DECISSION_REJECTED
        }],
        'manuscript_stage': _review_complete_stages(
          {**MANUSCRIPT_ID_FIELDS1, PERSON_ID: PERSON_ID1},
          contacted=pd.Timestamp('2017-01-01'),
          accepted=pd.Timestamp('2017-01-02'),
          reviewed=pd.Timestamp('2017-01-03')
        ),
        'manuscript_keyword': [MANUSCRIPT_KEYWORD1]
      }
      result = recommend_for_dataset(dataset, keywords=KEYWORD1, manuscript_no='')
      assert _potential_reviewers_person_ids(result['potential_reviewers']) == [PERSON_ID1]

    def test_matching_one_keyword_author_should_suggest_authors_with_unknown_decision_and_type(self):
      dataset = {
        'person': [PERSON1],
        'manuscript_version': [{
          **MANUSCRIPT_VERSION1,
          'decision': None,
          'manuscript_type': None
        }],
        'manuscript_author': [AUTHOR1],
        'manuscript_keyword': [MANUSCRIPT_KEYWORD1]
      }
      result = recommend_for_dataset(dataset, keywords=KEYWORD1, manuscript_no='')
      assert _potential_reviewers_person_ids(result['potential_reviewers']) == [PERSON_ID1]

    def test_matching_one_keyword_author_should_return_stats(self, logger):
      dataset = {
        'person': [PERSON1],
        'manuscript_version': [
          MANUSCRIPT_VERSION1,
          MANUSCRIPT_VERSION2,
          MANUSCRIPT_VERSION3,
          MANUSCRIPT_VERSION4,
          MANUSCRIPT_VERSION5
        ],
        'manuscript_author': [AUTHOR1],
        'manuscript_keyword': [MANUSCRIPT_KEYWORD1],
        # add two review durations (two stages each)
        # also add an open review (accepted)
        'manuscript_stage': (
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
        )
      }
      result = recommend_for_dataset(dataset, keywords=KEYWORD1, manuscript_no='')
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
      result_person = result['potential_reviewers'][0]['person']
      logger.debug("result_person: %s", PP.pformat(result_person))
      assert result_person['stats'] == {
        'overall': overall_stats,
        'last_12m': overall_stats
      }

    def test_matching_one_keyword_author_should_return_memberships(self, logger):
      dataset = {
        'person': [PERSON1],
        'person_membership': [MEMBERSHIP1],
        'manuscript_version': [MANUSCRIPT_VERSION1],
        'manuscript_author': [AUTHOR1],
        'manuscript_keyword': [MANUSCRIPT_KEYWORD1]
      }
      result = recommend_for_dataset(dataset, keywords=KEYWORD1, manuscript_no='')
      result_person = result['potential_reviewers'][0]['person']
      logger.debug("result_person: %s", PP.pformat(result_person))
      assert result_person.get('memberships') == [MEMBERSHIP1_RESULT]

    def test_matching_one_keyword_author_should_return_other_accepted_papers(self, logger):
      dataset = {
        'person': [PERSON1],
        'manuscript_version': [
          MANUSCRIPT_VERSION1, {
            **MANUSCRIPT_VERSION2,
            'decision': DECISSION_ACCEPTED
          }
        ],
        'manuscript_author': [
          AUTHOR1, {
            **AUTHOR1,
            **MANUSCRIPT_ID_FIELDS2
          }
        ],
        'manuscript_keyword': [MANUSCRIPT_KEYWORD1]
      }
      result = recommend_for_dataset(dataset, keywords=KEYWORD1, manuscript_no='')
      author_of_manuscripts = result['potential_reviewers'][0]['author_of_manuscripts']
      author_of_manuscript_ids = [m[MANUSCRIPT_ID] for m in author_of_manuscripts]
      logger.debug("author_of_manuscripts: %s", PP.pformat(author_of_manuscripts))
      logger.debug("author_of_manuscript_ids: %s", author_of_manuscript_ids)
      assert set(author_of_manuscript_ids) == set([
        MANUSCRIPT_VERSION1_RESULT[MANUSCRIPT_ID],
        MANUSCRIPT_VERSION2_RESULT[MANUSCRIPT_ID]
      ])

    def test_matching_one_keyword_author_should_not_return_other_draft_papers(self, logger):
      dataset = {
        'person': [PERSON1],
        'manuscript_version': [
          MANUSCRIPT_VERSION1, {
            **MANUSCRIPT_VERSION2,
            'decision': DECISSION_REJECTED
          }
        ],
        'manuscript_author': [
          AUTHOR1, {
            **AUTHOR1,
            **MANUSCRIPT_ID_FIELDS2
          }
        ],
        'manuscript_keyword': [MANUSCRIPT_KEYWORD1]
      }
      result = recommend_for_dataset(dataset, keywords=KEYWORD1, manuscript_no='')
      assert (
        [m[MANUSCRIPT_ID] for m in result['potential_reviewers'][0]['author_of_manuscripts']] ==
        [MANUSCRIPT_ID1]
      )

    def test_matching_one_keyword_author_should_return_papers_with_same_title_as_alternatives(
      self, logger):

      dataset = {
        'person': [PERSON1],
        'manuscript_version': [
          {
            **MANUSCRIPT_VERSION1,
            'title': MANUSCRIPT_TITLE1,
            'abstract': MANUSCRIPT_ABSTRACT1
          }, {
            **MANUSCRIPT_VERSION2,
            'title': MANUSCRIPT_TITLE1,
            'abstract': None
          }
        ],
        'manuscript_author': [
          AUTHOR1, {
            **AUTHOR1,
            **MANUSCRIPT_ID_FIELDS2
          }
        ],
        'manuscript_keyword': [MANUSCRIPT_KEYWORD1]
      }
      result = recommend_for_dataset(dataset, keywords=KEYWORD1, manuscript_no='')
      author_of_manuscripts = result['potential_reviewers'][0]['author_of_manuscripts']
      author_of_manuscript_ids = [m[MANUSCRIPT_ID] for m in author_of_manuscripts]
      logger.debug("author_of_manuscripts: %s", PP.pformat(author_of_manuscripts))
      logger.debug("author_of_manuscript_ids: %s", author_of_manuscript_ids)
      assert set(author_of_manuscript_ids) == set([
        MANUSCRIPT_VERSION1_RESULT[MANUSCRIPT_ID]
      ])

    def test_should_consider_previous_reviewer_as_potential_reviewer(self):
      dataset = {
        'person': [PERSON1],
        'manuscript_version': [MANUSCRIPT_VERSION1],
        'manuscript_stage': [MANUSCRIPT_HISTORY_REVIEW_COMPLETE1],
        'manuscript_keyword': [MANUSCRIPT_KEYWORD1]
      }
      result = recommend_for_dataset(dataset, keywords=KEYWORD1, manuscript_no='')
      assert [r['person'][PERSON_ID] for r in result['potential_reviewers']] == [PERSON_ID1]

    def test_should_return_reviewer_as_potential_reviewer_only_once(self):
      dataset = {
        'person': [PERSON1],
        'manuscript_version': [MANUSCRIPT_VERSION1],
        'manuscript_stage': [
          {
            **MANUSCRIPT_HISTORY_REVIEW_COMPLETE1,
            'stage_timestamp': pd.Timestamp('2017-01-01'),
          },
          {
            **MANUSCRIPT_HISTORY_REVIEW_COMPLETE1,
            'stage_timestamp': pd.Timestamp('2017-01-02'),
          }
        ],
        'manuscript_keyword': [MANUSCRIPT_KEYWORD1]
      }
      result = recommend_for_dataset(dataset, keywords=KEYWORD1, manuscript_no='')
      assert [
        r['person'][PERSON_ID] for r in result['potential_reviewers']
      ] == [PERSON_ID1]

  class TestRecommendReviewersByRole:
    def test_should_not_recommend_regular_reviewer_when_searching_for_senior_editor_via_keyword(self):
      # a regular reviewer doesn't have a role
      dataset = {
        'person': [PERSON1],
        'manuscript_version': [MANUSCRIPT_VERSION1],
        'manuscript_author': [AUTHOR1],
        'manuscript_keyword': [MANUSCRIPT_KEYWORD1]
      }
      result = recommend_for_dataset(
        dataset, keywords=KEYWORD1, manuscript_no=None,
        role=PersonRoles.SENIOR_EDITOR
      )
      person_ids = _potential_reviewers_person_ids(result['potential_reviewers'])
      assert person_ids == []

    def test_should_not_recommend_regular_reviewer_when_searching_for_senior_editor_via_manuscript_no(self):
      # a regular reviewer doesn't have a role
      dataset = {
        'person': [PERSON1],
        'manuscript_version': [MANUSCRIPT_VERSION1, MANUSCRIPT_VERSION2],
        'manuscript_author': [AUTHOR1],
        'manuscript_keyword': [MANUSCRIPT_KEYWORD1, {
          **MANUSCRIPT_KEYWORD1,
          **MANUSCRIPT_ID_FIELDS2
        }]
      }
      result = recommend_for_dataset(
        dataset, keywords=None, manuscript_no=MANUSCRIPT_ID2,
        role=PersonRoles.SENIOR_EDITOR
      )
      person_ids = _potential_reviewers_person_ids(result['potential_reviewers'])
      assert person_ids == []

    def test_should_not_recommend_reviewer_with_other_role_when_searching_for_senior_editor(self):
      dataset = {
        'person': [PERSON1],
        'person_role': [{PERSON_ID: PERSON_ID1, 'role': PersonRoles.OTHER}],
        'manuscript_version': [MANUSCRIPT_VERSION1],
        'manuscript_author': [AUTHOR1],
        'manuscript_keyword': [MANUSCRIPT_KEYWORD1]
      }
      result = recommend_for_dataset(
        dataset, keywords=KEYWORD1, manuscript_no=None,
        role=PersonRoles.SENIOR_EDITOR
      )
      person_ids = _potential_reviewers_person_ids(result['potential_reviewers'])
      assert person_ids == []

    def test_should_recommend_senior_editor_based_on_manuscript_keyword(self):
      dataset = {
        'person': [PERSON1],
        'person_role': [{PERSON_ID: PERSON_ID1, 'role': PersonRoles.SENIOR_EDITOR}],
        'manuscript_version': [MANUSCRIPT_VERSION1],
        'manuscript_author': [AUTHOR1],
        'manuscript_keyword': [MANUSCRIPT_KEYWORD1]
      }
      result = recommend_for_dataset(
        dataset, keywords=KEYWORD1, manuscript_no=None,
        role=PersonRoles.SENIOR_EDITOR
      )
      person_ids = _potential_reviewers_person_ids(result['potential_reviewers'])
      assert person_ids == [PERSON_ID1]

    def test_should_recommend_senior_editor_based_on_manuscript_keyword_via_manuscript_no(self):
      dataset = {
        'person': [PERSON1],
        'person_role': [{PERSON_ID: PERSON_ID1, 'role': PersonRoles.SENIOR_EDITOR}],
        'manuscript_version': [MANUSCRIPT_VERSION1, MANUSCRIPT_VERSION2],
        'manuscript_author': [AUTHOR1],
        'manuscript_keyword': [MANUSCRIPT_KEYWORD1, {
          **MANUSCRIPT_KEYWORD1,
          **MANUSCRIPT_ID_FIELDS2
        }]
      }
      result = recommend_for_dataset(
        dataset, keywords=None, manuscript_no=MANUSCRIPT_ID2,
        role=PersonRoles.SENIOR_EDITOR
      )
      person_ids = _potential_reviewers_person_ids(result['potential_reviewers'])
      assert person_ids == [PERSON_ID1]

    def test_should_recommend_previous_senior_editors_and_reflect_in_score(self):
      dataset = {
        'person': [PERSON1],
        'person_role': [{PERSON_ID: PERSON_ID1, 'role': PersonRoles.SENIOR_EDITOR}],
        'manuscript_version': [MANUSCRIPT_VERSION1, MANUSCRIPT_VERSION2],
        'manuscript_senior_editor': [{**MANUSCRIPT_ID_FIELDS1, 'person_id': PERSON_ID1}],
        'manuscript_keyword': [MANUSCRIPT_KEYWORD1, {
          **MANUSCRIPT_KEYWORD1,
          **MANUSCRIPT_ID_FIELDS2
        }]
      }
      result = recommend_for_dataset(
        dataset, keywords=None, manuscript_no=MANUSCRIPT_ID2,
        role=PersonRoles.SENIOR_EDITOR,
        recommend_relationship_types=[
          RelationshipTypes.AUTHOR,
          RelationshipTypes.EDITOR,
          RelationshipTypes.SENIOR_EDITOR,
          RelationshipTypes.REVIEWER
        ]
      )
      potential_reviewers = result['potential_reviewers']
      person_ids = _potential_reviewers_person_ids(potential_reviewers)
      assert person_ids == [PERSON_ID1]
      assert _potential_reviewer_scores_by_person_id(potential_reviewers) == {
        PERSON_ID1: 1.0
      }

    def test_should_recommend_based_on_stage_name(self):
      custom_stage = 'custom_stage'
      dataset = {
        'person': [PERSON1],
        'person_role': [{PERSON_ID: PERSON_ID1, 'role': PersonRoles.SENIOR_EDITOR}],
        'manuscript_version': [MANUSCRIPT_VERSION1, MANUSCRIPT_VERSION2],
        'manuscript_stage': [
          {
            **MANUSCRIPT_ID_FIELDS1,
            'person_id': PERSON_ID1,
            'stage_timestamp': pd.Timestamp('2017-01-01'),
            'stage_name': custom_stage
          }
        ],
        'manuscript_keyword': [MANUSCRIPT_KEYWORD1, {
          **MANUSCRIPT_KEYWORD1,
          **MANUSCRIPT_ID_FIELDS2
        }]
      }
      result = recommend_for_dataset(
        dataset, keywords=None, manuscript_no=MANUSCRIPT_ID2,
        role=PersonRoles.SENIOR_EDITOR,
        recommend_stage_names=[
          custom_stage
        ]
      )
      potential_reviewers = result['potential_reviewers']
      person_ids = _potential_reviewers_person_ids(potential_reviewers)
      assert person_ids == [PERSON_ID1]

    def test_should_recommend_senior_editor_based_on_person_keyword_and_reflect_in_score(self):
      dataset = {
        'person': [PERSON1],
        'person_role': [{PERSON_ID: PERSON_ID1, 'role': PersonRoles.SENIOR_EDITOR}],
        'person_keyword': [{PERSON_ID: PERSON_ID1, 'keyword': KEYWORD1}]
      }
      result = recommend_for_dataset(
        dataset, keywords=KEYWORD1, manuscript_no=None,
        role=PersonRoles.SENIOR_EDITOR
      )
      potential_reviewers = result['potential_reviewers']
      person_ids = _potential_reviewers_person_ids(potential_reviewers)
      assert person_ids == [PERSON_ID1]
      assert _potential_reviewer_scores_by_person_id(potential_reviewers) == {
        PERSON_ID1: 1.0
      }

  class TestAllKeywords:
    def test_should_include_manuscript_keywords_in_all_keywords(self):
      dataset = {
        'manuscript_version': [MANUSCRIPT_VERSION1],
        'manuscript_keyword': [MANUSCRIPT_KEYWORD1]
      }
      with create_recommend_reviewers(dataset) as recommend_reviewers:
        assert recommend_reviewers.get_all_keywords() == [KEYWORD1]

    def test_should_include_person_keywords_in_all_keywords(self):
      dataset = {
        'person': [PERSON1],
        'person_keyword': [{PERSON_ID: PERSON_ID1, 'keyword': KEYWORD1}]
      }
      with create_recommend_reviewers(dataset) as recommend_reviewers:
        assert recommend_reviewers.get_all_keywords() == [KEYWORD1]

  class TestUserHasRoleByEmail:
    def test_should_return_wether_user_has_role(self):
      dataset = {
        'person': [{**PERSON1, 'email': EMAIL_1}],
        'person_role': [{PERSON_ID: PERSON_ID1, 'role': ROLE_1}]
      }
      with create_recommend_reviewers(dataset) as recommend_reviewers:
        assert recommend_reviewers.user_has_role_by_email(email=EMAIL_1, role=ROLE_1) == True
        assert recommend_reviewers.user_has_role_by_email(email=EMAIL_1, role='other') == False
        assert recommend_reviewers.user_has_role_by_email(email='other', role=ROLE_1) == False

  class TestGetUserRolesByEmail:
    def test_should_return_roles_of_existing_user(self):
      dataset = {
        'person': [{**PERSON1, 'email': EMAIL_1}],
        'person_role': [{PERSON_ID: PERSON_ID1, 'role': ROLE_1}]
      }
      with create_recommend_reviewers(dataset) as recommend_reviewers:
        assert recommend_reviewers.get_user_roles_by_email(email=EMAIL_1) == {ROLE_1}
