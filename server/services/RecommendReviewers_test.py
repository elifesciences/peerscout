"""
Unit test
"""
import pprint

import pandas as pd

from .RecommendReviewers import RecommendReviewers, set_debug_enabled

set_debug_enabled(True)

MANUSCRIPT_NO = 'manuscript-no'
VERSION_NO = 'version-no'
MANUSCRIPT_VERSION_ID = 'manuscript-version-id'

MANUSCRIPT_ID_COLUMNS = [MANUSCRIPT_NO, VERSION_NO, MANUSCRIPT_VERSION_ID]
PERSON_ID_COLUMNS = ['person-id']

AUTHORS = pd.DataFrame(
  [],
  columns=MANUSCRIPT_ID_COLUMNS + ['author-person-id'])
PERSONS = pd.DataFrame(
  [],
  columns=PERSON_ID_COLUMNS + [
    'title', 'first-name', 'middle-name', 'last-name', 'institution', 'status', 'email'
  ])
EARLY_CAREER_REVIEWERS = pd.DataFrame(
  [],
  columns=PERSON_ID_COLUMNS + [
    'First subject area', 'Second subject area', 'ORCID',
    'first-name', 'last-name'
  ]
)
CROSSREF_PERSON_EXTRA = pd.DataFrame(
  [],
  columns=PERSON_ID_COLUMNS + ['doi', 'title', 'abstract', 'subject-areas', 'created-date']
)
PERSON_MEMBERSHIPS = pd.DataFrame(
  [],
  columns=PERSON_ID_COLUMNS + [
    'member-type', 'member-id'
  ]
)
PERSON_DATES_NOT_AVAILABLE = pd.DataFrame(
  [],
  columns=PERSON_ID_COLUMNS + [
    'dna-start-date', 'dna-end-date'
  ]
)
MANUSCRIPTS = pd.DataFrame(
  [],
  columns=[MANUSCRIPT_NO])
MANUSCRIPT_VERSIONS = pd.DataFrame(
  [],
  columns=MANUSCRIPT_ID_COLUMNS + [
    'title', 'decision', 'manuscript-type', 'abstract',
    'decision-date'
  ]
)
MANUSCRIPT_KEYWORDS = pd.DataFrame(
  [],
  columns=MANUSCRIPT_ID_COLUMNS + ['sequence', 'word'])
MANUSCRIPT_SUBJECT_AREAS = pd.DataFrame(
  [],
  columns=MANUSCRIPT_ID_COLUMNS + ['subject-area'])
MANUSCRIPT_HISTORY = pd.DataFrame(
  [],
  columns=MANUSCRIPT_ID_COLUMNS + ['stage-affective-person-id', 'stage-name', 'start-date'])

ABSTRACT_DOCVEC_COLUMN = 'abstract-sense2vec-docvecs'

ABSTRACT_DOCVECS = pd.DataFrame(
  [],
  columns=MANUSCRIPT_ID_COLUMNS + [ABSTRACT_DOCVEC_COLUMN])

CROSSREF_PERSON_EXTRA_SPACY_DOCVECS = pd.DataFrame(
  [],
  columns=['doi', ABSTRACT_DOCVEC_COLUMN]
)

CONTENT_DOCVECS = pd.DataFrame(
  [],
  columns=MANUSCRIPT_ID_COLUMNS + ['content-sense2vec-docvecs'])

ABSTRACT_DOCVEC_DATASET = 'manuscript-abstracts-sense2vec-lda-docvecs'
CROSSREF_PERSON_EXTRA_DOCVEC_DATASET = 'crossref-person-extra-sense2vec-lda-docvecs'
SUBJECT_AREAS_DATASET = 'manuscript-themes'

DATASETS = {
  'authors': AUTHORS,
  'persons': PERSONS,
  'early-career-reviewers': EARLY_CAREER_REVIEWERS,
  'crossref-person-extra': CROSSREF_PERSON_EXTRA,
  'person-memberships': PERSON_MEMBERSHIPS,
  'person-dates-not-available': PERSON_DATES_NOT_AVAILABLE,
  'manuscripts': MANUSCRIPTS,
  'manuscript-versions': MANUSCRIPT_VERSIONS,
  'manuscript-keywords': MANUSCRIPT_KEYWORDS,
  SUBJECT_AREAS_DATASET: MANUSCRIPT_SUBJECT_AREAS,
  'manuscript-history': MANUSCRIPT_HISTORY,
  ABSTRACT_DOCVEC_DATASET: ABSTRACT_DOCVECS,
  'article-content-spacy-docvecs': CONTENT_DOCVECS,
  CROSSREF_PERSON_EXTRA_DOCVEC_DATASET: CROSSREF_PERSON_EXTRA_SPACY_DOCVECS,
  CROSSREF_PERSON_EXTRA_DOCVEC_DATASET + '-model': {}
}

PERSON_ID1 = 'person1'
PERSON_ID2 = 'person2'
PERSON_ID3 = 'person3'

PERSON1 = {
  'person-id': PERSON_ID1,
  'first-name': 'John',
  'last-name': 'Smith',
  'status': 'Active'
}

PERSON1_RESULT = {
  **PERSON1,
  'is-early-career-reviewer': False,
  'memberships': [],
  'dates-not-available': [],
  'stats': {
    'overall': None,
    'last-12m': None
  }
}

PERSON2 = {
  **PERSON1,
  'person-id': PERSON_ID2,
  'first-name': 'Laura',
  'last-name': 'Laudson'
}

PERSON2_RESULT = {
  **PERSON1_RESULT,
  **PERSON2
}

PERSON3 = {
  **PERSON1,
  'person-id': PERSON_ID3,
  'first-name': 'Mike',
  'last-name': 'Michelson'
}

PERSON3_RESULT = {
  **PERSON1_RESULT,
  **PERSON3
}

MEMBERSHIP1_RESULT = {
  'member-type': 'memberme',
  'member-id': '12345'
}

MEMBERSHIP1 = {
  **MEMBERSHIP1_RESULT,
  'person-id': PERSON_ID1,
}

def version_id(manuscript_no, version_no):
  return '{}-{}'.format(manuscript_no, version_no)

MANUSCRIPT_NO1 = '12345'
VERSION_NO1 = 1
MANUSCRIPT_VERSION_ID1 = version_id(MANUSCRIPT_NO1, VERSION_NO1)
MANUSCRIPT_TITLE1 = 'Manuscript Title1'

MANUSCRIPT_NO2 = '22222'
VERSION_NO2 = 2
MANUSCRIPT_VERSION_ID2 = version_id(MANUSCRIPT_NO2, VERSION_NO2)
MANUSCRIPT_TITLE2 = 'Manuscript Title2'

MANUSCRIPT_NO3 = '33333'
VERSION_NO3 = 3
MANUSCRIPT_VERSION_ID3 = version_id(MANUSCRIPT_NO3, VERSION_NO3)
MANUSCRIPT_TITLE3 = 'Manuscript Title3'

MANUSCRIPT_ID_FIELDS1 = {
  MANUSCRIPT_NO: MANUSCRIPT_NO1,
  VERSION_NO: VERSION_NO1,
  MANUSCRIPT_VERSION_ID: MANUSCRIPT_VERSION_ID1
}

MANUSCRIPT_ID_FIELDS2 = {
  MANUSCRIPT_NO: MANUSCRIPT_NO2,
  VERSION_NO: VERSION_NO2,
  MANUSCRIPT_VERSION_ID: MANUSCRIPT_VERSION_ID2
}

MANUSCRIPT_ID_FIELDS3 = {
  MANUSCRIPT_NO: MANUSCRIPT_NO3,
  VERSION_NO: VERSION_NO3,
  MANUSCRIPT_VERSION_ID: MANUSCRIPT_VERSION_ID3
}

create_manuscript_id_fields = lambda i: ({
  MANUSCRIPT_NO: str(i),
  VERSION_NO: 1,
  MANUSCRIPT_VERSION_ID: version_id(str(i), 1)
})

MANUSCRIPT_ID_FIELDS4 = create_manuscript_id_fields(4)
MANUSCRIPT_ID_FIELDS5 = create_manuscript_id_fields(5)

DECISSION_ACCEPTED = 'Accept Full Submission'
DECISSION_REJECTED = 'Reject Full Submission'

TYPE_RESEARCH_ARTICLE = 'Research Article'

MANUSCRIPT_VERSION1_RESULT = {
  **MANUSCRIPT_ID_FIELDS1,
  'doi': None,
  'title': MANUSCRIPT_TITLE1,
  'decision': DECISSION_ACCEPTED,
  'manuscript-type': TYPE_RESEARCH_ARTICLE,
  'subject-areas': []
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

KEYWORD1 = 'keyword1'

MANUSCRIPT_KEYWORD1 = {
  **MANUSCRIPT_ID_FIELDS1,
  'word': KEYWORD1
}

SUBJECT_AREA1 = 'subject area1'
SUBJECT_AREA2 = 'subject area2'

MANUSCRIPT_SUBJECT_AREA1 = {
  **MANUSCRIPT_ID_FIELDS1,
  'subject-area': SUBJECT_AREA1
}

MANUSCRIPT_SUBJECT_AREA2 = {
  **MANUSCRIPT_ID_FIELDS1,
  'subject-area': SUBJECT_AREA2
}

DOCVEC1 = [1, 1]
DOCVEC2 = [2, 2]

ABSTRACT_DOCVEC1 = {
  **MANUSCRIPT_ID_FIELDS1,
  ABSTRACT_DOCVEC_COLUMN: DOCVEC1
}

ABSTRACT_DOCVEC2 = {
  **MANUSCRIPT_ID_FIELDS2,
  ABSTRACT_DOCVEC_COLUMN: DOCVEC2
}

DOI1 = 'doi/1'

CROSSREF_ABSTRACT_DOCVEC1 = {
  'doi': DOI1,
  ABSTRACT_DOCVEC_COLUMN: DOCVEC1
}

CROSSREF_ABSTRACT_DOCVEC2 = {
  'doi': DOI1,
  ABSTRACT_DOCVEC_COLUMN: DOCVEC1
}

AUTHOR1 = {
  **MANUSCRIPT_ID_FIELDS1,
  'author-person-id': PERSON_ID1
}

AUTHOR2 = {
  **MANUSCRIPT_ID_FIELDS1,
  'author-person-id': PERSON_ID2
}

AUTHOR3 = {
  **MANUSCRIPT_ID_FIELDS1,
  'author-person-id': PERSON_ID3
}

STAGE_CONTACTING_REVIEWERS = 'Contacting Reviewers'
STAGE_REVIEW_ACCEPTED = 'Reviewers Accept'
STAGE_REVIEW_DECLINE = 'Reviewers Decline'
STAGE_REVIEW_COMPLETE = 'Review Received'

MANUSCRIPT_HISTORY_REVIEW_COMPLETE1 = {
  **MANUSCRIPT_ID_FIELDS1,
  'stage-name': STAGE_REVIEW_COMPLETE,
  'stage-affective-person-id': PERSON_ID1
}

POTENTIAL_REVIEWER1 = {
  'person': PERSON1_RESULT,
  'scores': {
    'keyword': 1.0,
    'similarity': None,
    'by-manuscript': [{
      **MANUSCRIPT_ID_FIELDS1,
      'keyword': 1.0,
      'similarity': None
    }]
  }
}

POTENTIAL_REVIEWER2 = {
  **POTENTIAL_REVIEWER1,
  'person': PERSON2_RESULT
}

PP = pprint.PrettyPrinter(indent=2, width=40)

def test_no_match():
  recommend_reviewers = RecommendReviewers(DATASETS)
  result = recommend_reviewers.recommend(keywords='', manuscript_no='')
  assert result == {
    'potential-reviewers': [],
    'matching-manuscripts': []
  }

def test_matching_manuscript():
  datasets = dict(DATASETS)
  datasets['persons'] = pd.DataFrame([
    PERSON1
  ], columns=PERSONS.columns)
  datasets['manuscript-versions'] = pd.DataFrame([
    MANUSCRIPT_VERSION1
  ], columns=MANUSCRIPT_VERSIONS.columns)
  datasets['manuscript-keywords'] = pd.DataFrame([
    MANUSCRIPT_KEYWORD1
  ], columns=MANUSCRIPT_KEYWORDS.columns)
  recommend_reviewers = RecommendReviewers(datasets)
  result = recommend_reviewers.recommend(keywords='', manuscript_no=MANUSCRIPT_NO1)
  assert result == {
    'potential-reviewers': [],
    'matching-manuscripts': [{
      **MANUSCRIPT_VERSION1_RESULT,
      'authors': [],
      'reviewers': []
    }]
  }

def test_matching_manuscript_should_return_manuscript_only_once():
  datasets = dict(DATASETS)
  datasets['persons'] = pd.DataFrame([
    PERSON1
  ], columns=PERSONS.columns)
  datasets['manuscript-versions'] = pd.DataFrame([
    MANUSCRIPT_VERSION1, MANUSCRIPT_VERSION1
  ], columns=MANUSCRIPT_VERSIONS.columns)
  datasets['manuscript-keywords'] = pd.DataFrame([
    MANUSCRIPT_KEYWORD1, MANUSCRIPT_KEYWORD1
  ], columns=MANUSCRIPT_KEYWORDS.columns)
  recommend_reviewers = RecommendReviewers(datasets)
  result = recommend_reviewers.recommend(keywords='', manuscript_no=MANUSCRIPT_NO1)
  print("result:", result)
  assert result == {
    'potential-reviewers': [],
    'matching-manuscripts': [{
      **MANUSCRIPT_VERSION1_RESULT,
      'authors': [],
      'reviewers': []
    }]
  }

def test_matching_manuscript_should_include_subject_areas():
  datasets = dict(DATASETS)
  datasets['persons'] = pd.DataFrame([
    PERSON1
  ], columns=PERSONS.columns)
  datasets['manuscript-versions'] = pd.DataFrame([
    MANUSCRIPT_VERSION1
  ], columns=MANUSCRIPT_VERSIONS.columns)
  datasets['manuscript-keywords'] = pd.DataFrame([
    MANUSCRIPT_KEYWORD1
  ], columns=MANUSCRIPT_KEYWORDS.columns)
  datasets[SUBJECT_AREAS_DATASET] = pd.DataFrame([
    MANUSCRIPT_SUBJECT_AREA1,
    MANUSCRIPT_SUBJECT_AREA2
  ], columns=MANUSCRIPT_SUBJECT_AREAS.columns)
  recommend_reviewers = RecommendReviewers(datasets)
  result = recommend_reviewers.recommend(keywords='', manuscript_no=MANUSCRIPT_NO1)
  subject_areas = result['matching-manuscripts'][0]['subject-areas']
  assert subject_areas == [SUBJECT_AREA1, SUBJECT_AREA2]

def test_matching_manuscript_with_docvecs():
  datasets = dict(DATASETS)
  datasets['persons'] = pd.DataFrame([
    PERSON1
  ], columns=PERSONS.columns)
  datasets['manuscript-versions'] = pd.DataFrame([
    MANUSCRIPT_VERSION1
  ], columns=MANUSCRIPT_VERSIONS.columns)
  datasets['manuscript-keywords'] = pd.DataFrame([
    MANUSCRIPT_KEYWORD1
  ], columns=MANUSCRIPT_KEYWORDS.columns)
  datasets[ABSTRACT_DOCVEC_DATASET] = pd.DataFrame([
    ABSTRACT_DOCVEC1
  ], columns=ABSTRACT_DOCVECS.columns)
  recommend_reviewers = RecommendReviewers(datasets)
  recommend_reviewers.recommend(keywords='', manuscript_no=MANUSCRIPT_NO1)

def test_matching_manuscript_with_none_docvecs():
  datasets = dict(DATASETS)
  datasets['persons'] = pd.DataFrame([
    PERSON1
  ], columns=PERSONS.columns)
  datasets['manuscript-versions'] = pd.DataFrame([
    MANUSCRIPT_VERSION1
  ], columns=MANUSCRIPT_VERSIONS.columns)
  datasets['manuscript-keywords'] = pd.DataFrame([
    MANUSCRIPT_KEYWORD1
  ], columns=MANUSCRIPT_KEYWORDS.columns)
  datasets[ABSTRACT_DOCVEC_DATASET] = pd.DataFrame([
    ABSTRACT_DOCVEC1,
    {
      **ABSTRACT_DOCVEC2,
      ABSTRACT_DOCVEC_COLUMN: None
    }
  ], columns=ABSTRACT_DOCVECS.columns)
  recommend_reviewers = RecommendReviewers(datasets)
  recommend_reviewers.recommend(keywords='', manuscript_no=MANUSCRIPT_NO1)

def test_matching_manuscript_should_recommend_early_career_reviewer_and_return_similarity():
  datasets = dict(DATASETS)
  datasets['persons'] = pd.DataFrame([
    PERSON1
  ], columns=PERSONS.columns)
  datasets['manuscript-versions'] = pd.DataFrame([
    MANUSCRIPT_VERSION1
  ], columns=MANUSCRIPT_VERSIONS.columns)
  datasets['manuscript-keywords'] = pd.DataFrame([
    MANUSCRIPT_KEYWORD1
  ], columns=MANUSCRIPT_KEYWORDS.columns)
  datasets[SUBJECT_AREAS_DATASET] = pd.DataFrame([{
    **MANUSCRIPT_ID_FIELDS1,
    'subject-area': SUBJECT_AREA1
  }], columns=MANUSCRIPT_SUBJECT_AREAS.columns)
  datasets[ABSTRACT_DOCVEC_DATASET] = pd.DataFrame([
    ABSTRACT_DOCVEC1
  ], columns=ABSTRACT_DOCVECS.columns)
  datasets[CROSSREF_PERSON_EXTRA_DOCVEC_DATASET] = pd.DataFrame([
    CROSSREF_ABSTRACT_DOCVEC1
  ], columns=CROSSREF_PERSON_EXTRA_SPACY_DOCVECS.columns)
  datasets['early-career-reviewers'] = pd.DataFrame([{
    'person-id': PERSON_ID2,
    'first-name': 'Early',
    'last-name': 'Bird',
    'ORCID': '',
    'First subject area': SUBJECT_AREA1,
    'Second subject area': ''
  }], columns=EARLY_CAREER_REVIEWERS.columns)
  datasets['crossref-person-extra'] = pd.DataFrame([{
    'person-id': PERSON_ID2,
    'doi': DOI1,
    'subject-areas': str([])
  }], columns=CROSSREF_PERSON_EXTRA.columns)
  recommend_reviewers = RecommendReviewers(datasets)
  result = recommend_reviewers.recommend(keywords='', manuscript_no=MANUSCRIPT_NO1)
  print("result:", PP.pformat(result))
  recommended_person_ids = [r['person']['person-id'] for r in result['potential-reviewers']]
  assert recommended_person_ids == [PERSON_ID2]
  similarities = [r['scores']['similarity'] for r in result['potential-reviewers']]
  assert len(similarities) == 1
  assert abs(similarities[0] - 1) < 0.01

def test_matching_manuscript_should_return_draft_version_with_authors():
  datasets = dict(DATASETS)
  datasets['persons'] = pd.DataFrame([
    PERSON1
  ], columns=PERSONS.columns)
  datasets['authors'] = pd.DataFrame([
    AUTHOR1
  ], columns=AUTHORS.columns)
  datasets['manuscript-versions'] = pd.DataFrame([{
    **MANUSCRIPT_VERSION1,
    'decision': DECISSION_REJECTED
  }], columns=MANUSCRIPT_VERSIONS.columns)
  datasets['manuscript-keywords'] = pd.DataFrame([
    MANUSCRIPT_KEYWORD1
  ], columns=MANUSCRIPT_KEYWORDS.columns)
  recommend_reviewers = RecommendReviewers(datasets)
  result = recommend_reviewers.recommend(keywords='', manuscript_no=MANUSCRIPT_NO1)
  print("result:", PP.pformat(result))
  assert result == {
    'potential-reviewers': [],
    'matching-manuscripts': [{
      **MANUSCRIPT_VERSION1_RESULT,
      'decision': DECISSION_REJECTED,
      'authors': [PERSON1_RESULT],
      'reviewers': []
    }]
  }

def test_matching_manuscript_should_not_recommend_its_authors():
  datasets = dict(DATASETS)
  datasets['persons'] = pd.DataFrame([
    PERSON1,
    PERSON2
  ], columns=PERSONS.columns)
  datasets['manuscript-versions'] = pd.DataFrame([
    MANUSCRIPT_VERSION1,
    MANUSCRIPT_VERSION2
  ], columns=MANUSCRIPT_VERSIONS.columns)
  datasets['manuscript-keywords'] = pd.DataFrame([
    MANUSCRIPT_KEYWORD1,
    {
      **MANUSCRIPT_KEYWORD1,
      **MANUSCRIPT_ID_FIELDS2
    }
  ], columns=MANUSCRIPT_KEYWORDS.columns)
  datasets['authors'] = pd.DataFrame([
    AUTHOR1,
    {
      **AUTHOR1,
      **MANUSCRIPT_ID_FIELDS2
    },
    {
      **AUTHOR2,
      **MANUSCRIPT_ID_FIELDS2
    }
  ], columns=AUTHORS.columns)
  recommend_reviewers = RecommendReviewers(datasets)
  result = recommend_reviewers.recommend(keywords='', manuscript_no=MANUSCRIPT_NO1)
  print("result:", PP.pformat(result))
  recommended_person_ids = [r['person']['person-id'] for r in result['potential-reviewers']]
  assert recommended_person_ids == [PERSON_ID2]

def test_matching_manuscript_should_only_recommend_authors_of_matching_subject_areas():
  datasets = dict(DATASETS)
  datasets['persons'] = pd.DataFrame([
    PERSON1,
    PERSON2,
    PERSON3
  ], columns=PERSONS.columns)
  datasets['manuscript-versions'] = pd.DataFrame([
    MANUSCRIPT_VERSION1,
    MANUSCRIPT_VERSION2,
    MANUSCRIPT_VERSION3
  ], columns=MANUSCRIPT_VERSIONS.columns)
  datasets['manuscript-keywords'] = pd.DataFrame([
    MANUSCRIPT_KEYWORD1,
    {
      **MANUSCRIPT_KEYWORD1,
      **MANUSCRIPT_ID_FIELDS2
    },
    {
      **MANUSCRIPT_KEYWORD1,
      **MANUSCRIPT_ID_FIELDS3
    }
  ], columns=MANUSCRIPT_KEYWORDS.columns)
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
  datasets['authors'] = pd.DataFrame([
    AUTHOR1,
    {
      **AUTHOR2,
      **MANUSCRIPT_ID_FIELDS2
    },
    {
      **AUTHOR3,
      **MANUSCRIPT_ID_FIELDS3
    }
  ], columns=AUTHORS.columns)
  recommend_reviewers = RecommendReviewers(datasets)
  result = recommend_reviewers.recommend(keywords='', manuscript_no=MANUSCRIPT_NO1)
  print("result:", PP.pformat(result))
  recommended_person_ids = [r['person']['person-id'] for r in result['potential-reviewers']]
  assert recommended_person_ids == [PERSON_ID3]

def test_matching_one_keyword_author():
  datasets = dict(DATASETS)
  datasets['persons'] = pd.DataFrame([
    PERSON1
  ], columns=PERSONS.columns)
  datasets['authors'] = pd.DataFrame([
    AUTHOR1
  ], columns=AUTHORS.columns)
  datasets['manuscript-versions'] = pd.DataFrame([
    MANUSCRIPT_VERSION1
  ], columns=MANUSCRIPT_VERSIONS.columns)
  datasets['manuscript-keywords'] = pd.DataFrame([
    MANUSCRIPT_KEYWORD1
  ], columns=MANUSCRIPT_KEYWORDS.columns)
  recommend_reviewers = RecommendReviewers(datasets)
  result = recommend_reviewers.recommend(keywords=KEYWORD1, manuscript_no='')
  print("result:", PP.pformat(result))
  assert result == {
    'potential-reviewers': [{
      **POTENTIAL_REVIEWER1,
      'author-of-manuscripts': [{
        **MANUSCRIPT_VERSION1_RESULT,
        'authors': [PERSON1_RESULT],
        'reviewers': []
      }],
      'reviewer-of-manuscripts': []
    }],
    'matching-manuscripts': []
  }

def test_matching_one_keyword_author_should_not_return_author_of_rejected_manuscripts():
  datasets = dict(DATASETS)
  datasets['persons'] = pd.DataFrame([
    PERSON1
  ], columns=PERSONS.columns)
  datasets['authors'] = pd.DataFrame([
    AUTHOR1
  ], columns=AUTHORS.columns)
  datasets['manuscript-versions'] = pd.DataFrame([{
    **MANUSCRIPT_VERSION1,
    'decision': DECISSION_REJECTED
  }], columns=MANUSCRIPT_VERSIONS.columns)
  datasets['manuscript-keywords'] = pd.DataFrame([
    MANUSCRIPT_KEYWORD1
  ], columns=MANUSCRIPT_KEYWORDS.columns)
  recommend_reviewers = RecommendReviewers(datasets)
  result = recommend_reviewers.recommend(keywords=KEYWORD1, manuscript_no='')
  print("result:", PP.pformat(result))
  assert result == {
    'potential-reviewers': [],
    'matching-manuscripts': []
  }

def test_matching_one_keyword_author_should_return_stats():
  datasets = dict(DATASETS)
  datasets['persons'] = pd.DataFrame([
    PERSON1
  ], columns=PERSONS.columns)
  datasets['authors'] = pd.DataFrame([
    AUTHOR1
  ], columns=AUTHORS.columns)
  datasets['manuscript-versions'] = pd.DataFrame([
    MANUSCRIPT_VERSION1
  ], columns=MANUSCRIPT_VERSIONS.columns)
  datasets['manuscript-keywords'] = pd.DataFrame([
    MANUSCRIPT_KEYWORD1
  ], columns=MANUSCRIPT_KEYWORDS.columns)
  # add two review durations (two stages each)
  # also add an open review (accepted)
  datasets['manuscript-history'] = pd.DataFrame([{
    **MANUSCRIPT_ID_FIELDS1,
    'stage-affective-person-id': PERSON_ID1,
    'stage-name': STAGE_REVIEW_ACCEPTED,
    'start-date': pd.Timestamp('2017-01-01')
  }, {
    **MANUSCRIPT_ID_FIELDS1,
    'stage-affective-person-id': PERSON_ID1,
    'stage-name': STAGE_REVIEW_COMPLETE,
    'start-date': pd.Timestamp('2017-01-02')
  }, {
    **MANUSCRIPT_ID_FIELDS2,
    'stage-affective-person-id': PERSON_ID1,
    'stage-name': STAGE_REVIEW_ACCEPTED,
    'start-date': pd.Timestamp('2017-02-01')
  }, {
    **MANUSCRIPT_ID_FIELDS2,
    'stage-affective-person-id': PERSON_ID1,
    'stage-name': STAGE_REVIEW_COMPLETE,
    'start-date': pd.Timestamp('2017-02-03')
  }, {
    **MANUSCRIPT_ID_FIELDS3,
    'stage-affective-person-id': PERSON_ID1,
    'stage-name': STAGE_REVIEW_ACCEPTED,
    'start-date': pd.Timestamp('2017-02-01')
  }, {
    **MANUSCRIPT_ID_FIELDS4,
    'stage-affective-person-id': PERSON_ID1,
    'stage-name': STAGE_CONTACTING_REVIEWERS,
    'start-date': pd.Timestamp('2017-02-01')
  }], columns=MANUSCRIPT_HISTORY.columns)
  recommend_reviewers = RecommendReviewers(datasets)
  review_duration = {
    'min': 1.0,
    'mean': 1.5,
    'max': 2,
    'count': 2
  }
  overall_stats = {
    'review-duration': review_duration,
    'reviews-in-progress': 1,
    'waiting-to-be-accepted': 1,
    'declined': 0
  }
  result = recommend_reviewers.recommend(keywords=KEYWORD1, manuscript_no='')
  result_person = result['potential-reviewers'][0]['person']
  print("result_person:", PP.pformat(result_person))
  assert result_person['stats'] == {
    'overall': overall_stats,
    'last-12m': overall_stats
  }

def test_matching_one_keyword_author_should_return_memberships():
  datasets = dict(DATASETS)
  datasets['persons'] = pd.DataFrame([
    PERSON1
  ], columns=PERSONS.columns)
  datasets['person-memberships'] = pd.DataFrame([
    MEMBERSHIP1,
  ], columns=PERSON_MEMBERSHIPS.columns)
  datasets['authors'] = pd.DataFrame([
    AUTHOR1
  ], columns=AUTHORS.columns)
  datasets['manuscript-versions'] = pd.DataFrame([
    MANUSCRIPT_VERSION1
  ], columns=MANUSCRIPT_VERSIONS.columns)
  datasets['manuscript-keywords'] = pd.DataFrame([
    MANUSCRIPT_KEYWORD1
  ], columns=MANUSCRIPT_KEYWORDS.columns)
  recommend_reviewers = RecommendReviewers(datasets)
  person_with_memberships = {
    **PERSON1_RESULT,
    'memberships': [MEMBERSHIP1_RESULT]
  }
  result = recommend_reviewers.recommend(keywords=KEYWORD1, manuscript_no='')
  result_person = result['potential-reviewers'][0]['person']
  print("result_person:", PP.pformat(result_person))
  assert result_person == person_with_memberships

def test_matching_one_keyword_author_should_return_other_accepted_papers():
  datasets = dict(DATASETS)
  datasets['persons'] = pd.DataFrame([
    PERSON1
  ], columns=PERSONS.columns)
  datasets['authors'] = pd.DataFrame([
    AUTHOR1, {
      **AUTHOR1,
      **MANUSCRIPT_ID_FIELDS2
    }
  ], columns=AUTHORS.columns)
  datasets['manuscript-versions'] = pd.DataFrame([
    MANUSCRIPT_VERSION1, {
      **MANUSCRIPT_VERSION2,
      'decision': DECISSION_ACCEPTED
    }
  ], columns=MANUSCRIPT_VERSIONS.columns)
  datasets['manuscript-keywords'] = pd.DataFrame([
    MANUSCRIPT_KEYWORD1
  ], columns=MANUSCRIPT_KEYWORDS.columns)
  recommend_reviewers = RecommendReviewers(datasets)
  result = recommend_reviewers.recommend(keywords=KEYWORD1, manuscript_no='')
  author_of_manuscripts = result['potential-reviewers'][0]['author-of-manuscripts']
  author_of_manuscript_ids = [m[MANUSCRIPT_NO] for m in author_of_manuscripts]
  print("author_of_manuscripts:", PP.pformat(author_of_manuscripts))
  print("author_of_manuscript_ids:", author_of_manuscript_ids)
  assert set(author_of_manuscript_ids) == set([
    MANUSCRIPT_VERSION1_RESULT[MANUSCRIPT_NO],
    MANUSCRIPT_VERSION2_RESULT[MANUSCRIPT_NO]
  ])

def test_matching_one_keyword_author_should_not_return_other_draft_papers():
  datasets = dict(DATASETS)
  datasets['persons'] = pd.DataFrame([
    PERSON1
  ], columns=PERSONS.columns)
  datasets['authors'] = pd.DataFrame([
    AUTHOR1, {
      **AUTHOR1,
      **MANUSCRIPT_ID_FIELDS2
    }
  ], columns=AUTHORS.columns)
  datasets['manuscript-versions'] = pd.DataFrame([
    MANUSCRIPT_VERSION1, {
      **MANUSCRIPT_VERSION2,
      'decision': DECISSION_REJECTED
    }
  ], columns=MANUSCRIPT_VERSIONS.columns)
  datasets['manuscript-keywords'] = pd.DataFrame([
    MANUSCRIPT_KEYWORD1
  ], columns=MANUSCRIPT_KEYWORDS.columns)
  recommend_reviewers = RecommendReviewers(datasets)
  result = recommend_reviewers.recommend(keywords=KEYWORD1, manuscript_no='')
  print("result:", result)
  assert result == {
    'potential-reviewers': [{
      **POTENTIAL_REVIEWER1,
      'author-of-manuscripts': [{
        **MANUSCRIPT_VERSION1_RESULT,
        'authors': [PERSON1_RESULT],
        'reviewers': []
      }],
      'reviewer-of-manuscripts': []
    }],
    'matching-manuscripts': []
  }

def test_matching_one_keyword_author_should_return_author_only_once():
  datasets = dict(DATASETS)
  datasets['persons'] = pd.DataFrame([
    PERSON1
  ], columns=PERSONS.columns)
  datasets['authors'] = pd.DataFrame([
    AUTHOR1,
    AUTHOR1
  ], columns=AUTHORS.columns)
  datasets['manuscript-versions'] = pd.DataFrame([
    MANUSCRIPT_VERSION1
  ], columns=MANUSCRIPT_VERSIONS.columns)
  datasets['manuscript-keywords'] = pd.DataFrame([
    MANUSCRIPT_KEYWORD1,
    MANUSCRIPT_KEYWORD1
  ], columns=MANUSCRIPT_KEYWORDS.columns)
  recommend_reviewers = RecommendReviewers(datasets)
  result = recommend_reviewers.recommend(keywords=KEYWORD1, manuscript_no='')
  print("result:", result)
  assert result == {
    'potential-reviewers': [{
      **POTENTIAL_REVIEWER1,
      'author-of-manuscripts': [{
        **MANUSCRIPT_VERSION1_RESULT,
        'authors': [PERSON1_RESULT],
        'reviewers': []
      }],
      'reviewer-of-manuscripts': []
    }],
    'matching-manuscripts': []
  }

def test_matching_one_keyword_previous_reviewer():
  datasets = dict(DATASETS)
  datasets['persons'] = pd.DataFrame([
    PERSON1
  ], columns=PERSONS.columns)
  datasets['manuscript-versions'] = pd.DataFrame([
    MANUSCRIPT_VERSION1
  ], columns=MANUSCRIPT_VERSIONS.columns)
  datasets['manuscript-history'] = pd.DataFrame([
    MANUSCRIPT_HISTORY_REVIEW_COMPLETE1
  ], columns=MANUSCRIPT_HISTORY.columns)
  datasets['manuscript-keywords'] = pd.DataFrame([
    MANUSCRIPT_KEYWORD1
  ], columns=MANUSCRIPT_KEYWORDS.columns)
  recommend_reviewers = RecommendReviewers(datasets)
  result = recommend_reviewers.recommend(keywords=KEYWORD1, manuscript_no='')
  expected = {
    'potential-reviewers': [{
      **POTENTIAL_REVIEWER1,
      'author-of-manuscripts': [],
      'reviewer-of-manuscripts': [{
        **MANUSCRIPT_VERSION1_RESULT,
        'authors': [],
        'reviewers': [PERSON1_RESULT]
      }]
    }],
    'matching-manuscripts': []
  }
  print("result:", PP.pformat(result))
  print("expected:", PP.pformat(result))
  assert result == expected

def test_matching_one_keyword_previous_reviewer_should_return_reviewer_only_once():
  datasets = dict(DATASETS)
  datasets['persons'] = pd.DataFrame([
    PERSON1
  ], columns=PERSONS.columns)
  datasets['manuscript-versions'] = pd.DataFrame([
    MANUSCRIPT_VERSION1
  ], columns=MANUSCRIPT_VERSIONS.columns)
  datasets['manuscript-history'] = pd.DataFrame([
    MANUSCRIPT_HISTORY_REVIEW_COMPLETE1,
    MANUSCRIPT_HISTORY_REVIEW_COMPLETE1
  ], columns=MANUSCRIPT_HISTORY.columns)
  datasets['manuscript-keywords'] = pd.DataFrame([
    MANUSCRIPT_KEYWORD1,
    MANUSCRIPT_KEYWORD1
  ], columns=MANUSCRIPT_KEYWORDS.columns)
  recommend_reviewers = RecommendReviewers(datasets)
  result = recommend_reviewers.recommend(keywords=KEYWORD1, manuscript_no='')
  print("result:", PP.pformat(result))
  assert\
    [
      r['person']['person-id']
      for r in result['potential-reviewers']
    ] == [PERSON_ID1]
  assert\
    [
      r['person-id']
      for r in result['potential-reviewers'][0]\
        ['reviewer-of-manuscripts'][0]['reviewers']
    ] == [PERSON_ID1]
