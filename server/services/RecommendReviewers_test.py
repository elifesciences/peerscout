"""
Unit test
"""
import pprint

import pandas as pd

from .RecommendReviewers import RecommendReviewers

MANUSCRIPT_ID_COLUMNS = ['base-manuscript-number', 'manuscript-number', 'version-key']
PERSON_ID_COLUMNS = ['person-id']

AUTHORS = pd.DataFrame(
  [],
  columns=MANUSCRIPT_ID_COLUMNS + ['author-person-id'])
PERSONS = pd.DataFrame(
  [],
  columns=PERSON_ID_COLUMNS + [
    'title', 'first-name', 'middle-name', 'last-name', 'institution', 'status'
  ])
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
  columns=['manuscript-number'])
MANUSCRIPT_VERSIONS = pd.DataFrame(
  [],
  columns=MANUSCRIPT_ID_COLUMNS + ['title', 'decision'])
MANUSCRIPT_KEYWORDS = pd.DataFrame(
  [],
  columns=MANUSCRIPT_ID_COLUMNS + ['sequence', 'word'])
MANUSCRIPT_HISTORY = pd.DataFrame(
  [],
  columns=MANUSCRIPT_ID_COLUMNS + ['stage-affective-person-id', 'stage-name', 'start-date'])

DATASETS = {
  'authors': AUTHORS,
  'persons': PERSONS,
  'persons-current': PERSONS,
  'person-memberships': PERSON_MEMBERSHIPS,
  'person-dates-not-available': PERSON_DATES_NOT_AVAILABLE,
  'manuscripts': MANUSCRIPTS,
  'manuscript-versions': MANUSCRIPT_VERSIONS,
  'manuscript-keywords': MANUSCRIPT_KEYWORDS,
  'manuscript-history': MANUSCRIPT_HISTORY
}

PERSON_ID1 = 'person1'

PERSON1 = {
  'person-id': 'person1',
  'first-name': 'John',
  'last-name': 'Smith',
  'status': 'Active'
}

PERSON1_RESULT = {
  **PERSON1,
  'memberships': [],
  'dates-not-available': [],
  'stats': {
    'review-duration': None
  }
}

MEMBERSHIP1_RESULT = {
  'member-type': 'memberme',
  'member-id': '12345'
}

MEMBERSHIP1 = {
  **MEMBERSHIP1_RESULT,
  'person-id': PERSON_ID1,
}

MANUSCRIPT_NO1 = '12345'
MANUSCRIPT_NUMBER1 = 'some-prefix-' + MANUSCRIPT_NO1
VERSION_KEY1 = '11111|0'
MANUSCRIPT_TITLE1 = 'Manuscript Title1'

MANUSCRIPT_NO2 = '22222'
MANUSCRIPT_NUMBER2 = 'some-prefix-' + MANUSCRIPT_NO2
VERSION_KEY2 = '22222|0'
MANUSCRIPT_TITLE2 = 'Manuscript Title2'

MANUSCRIPT_ID_FIELDS1 = {
  'base-manuscript-number': MANUSCRIPT_NUMBER1,
  'manuscript-number': MANUSCRIPT_NUMBER1,
  'version-key': VERSION_KEY1
}

MANUSCRIPT_ID_FIELDS2 = {
  'base-manuscript-number': MANUSCRIPT_NUMBER2,
  'manuscript-number': MANUSCRIPT_NUMBER2,
  'version-key': VERSION_KEY2
}

DECISSION_ACCEPTED = 'Accept Full Submission'
DECISSION_REJECTED = 'Reject Full Submission'

MANUSCRIPT_VERSION1_RESULT = {
  **MANUSCRIPT_ID_FIELDS1,
  'title': MANUSCRIPT_TITLE1
}

MANUSCRIPT_VERSION1 = {
  **MANUSCRIPT_VERSION1_RESULT,
  'decision': DECISSION_ACCEPTED
}

MANUSCRIPT_VERSION2_RESULT = {
  **MANUSCRIPT_ID_FIELDS2,
  'title': MANUSCRIPT_TITLE2
}

MANUSCRIPT_VERSION2 = {
  **MANUSCRIPT_VERSION2_RESULT,
  'decision': DECISSION_ACCEPTED
}

KEYWORD1 = 'keyword1'

MANUSCRIPT_KEYWORD1 = {
  **MANUSCRIPT_ID_FIELDS1,
  'word': KEYWORD1
}

AUTHOR1 = {
  **MANUSCRIPT_ID_FIELDS1,
  'author-person-id': PERSON_ID1
}

STAGE_REVIEW_ACCEPTED = 'Reviewers Accept'
STAGE_REVIEW_COMPLETE = 'Review Received'

MANUSCRIPT_HISTORY_REVIEW_COMPLETE1 = {
  **MANUSCRIPT_ID_FIELDS1,
  'stage-name': STAGE_REVIEW_COMPLETE,
  'stage-affective-person-id': PERSON_ID1
}

POTENTIAL_REVIEWER1 = {
  'person': PERSON1_RESULT,
  'scores': {
    'keyword': 1
  }
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
  datasets['persons-current'] = pd.DataFrame([
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
  datasets['persons-current'] = pd.DataFrame([
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

def test_matching_manuscript_should_not_return_draft_version():
  datasets = dict(DATASETS)
  datasets['persons-current'] = pd.DataFrame([
    PERSON1
  ], columns=PERSONS.columns)
  datasets['manuscript-versions'] = pd.DataFrame([{
    **MANUSCRIPT_VERSION1,
    'decision': DECISSION_REJECTED
  }], columns=MANUSCRIPT_VERSIONS.columns)
  datasets['manuscript-keywords'] = pd.DataFrame([
    MANUSCRIPT_KEYWORD1
  ], columns=MANUSCRIPT_KEYWORDS.columns)
  recommend_reviewers = RecommendReviewers(datasets)
  result = recommend_reviewers.recommend(keywords='', manuscript_no=MANUSCRIPT_NO1)
  assert result == {
    'potential-reviewers': [],
    'matching-manuscripts': []
  }

def test_matching_one_keyword_author():
  datasets = dict(DATASETS)
  datasets['persons-current'] = pd.DataFrame([
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

def test_matching_one_keyword_author_should_return_stats():
  datasets = dict(DATASETS)
  datasets['persons-current'] = pd.DataFrame([
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
  }], columns=MANUSCRIPT_HISTORY.columns)
  recommend_reviewers = RecommendReviewers(datasets)
  person_with_stats = {
    **PERSON1_RESULT,
    'stats': {
      'review-duration': {
        'min': 1.0,
        'mean': 1.5,
        'max': 2
      }
    }
  }
  result = recommend_reviewers.recommend(keywords=KEYWORD1, manuscript_no='')
  result_person = result['potential-reviewers'][0]['person']
  print("result_person:", PP.pformat(result_person))
  assert result_person == person_with_stats

def test_matching_one_keyword_author_should_return_memberships():
  datasets = dict(DATASETS)
  datasets['persons-current'] = pd.DataFrame([
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
  datasets['persons-current'] = pd.DataFrame([
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
  author_of_manuscript_ids = [m['version-key'] for m in author_of_manuscripts]
  print("author_of_manuscripts:", PP.pformat(author_of_manuscripts))
  print("author_of_manuscript_ids:", author_of_manuscript_ids)
  assert set(author_of_manuscript_ids) == set([
    MANUSCRIPT_VERSION1_RESULT['version-key'],
    MANUSCRIPT_VERSION2_RESULT['version-key']
  ])

def test_matching_one_keyword_author_should_not_return_other_draft_papers():
  datasets = dict(DATASETS)
  datasets['persons-current'] = pd.DataFrame([
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
  datasets['persons-current'] = pd.DataFrame([
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
  datasets['persons-current'] = pd.DataFrame([
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
  print("result:", result)
  assert result == {
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

def test_matching_one_keyword_previous_reviewer_should_return_reviewer_only_once():
  datasets = dict(DATASETS)
  datasets['persons-current'] = pd.DataFrame([
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
  assert result == {
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
