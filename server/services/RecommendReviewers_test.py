"""
Unit test
"""
import pandas as pd

from .RecommendReviewers import RecommendReviewers

MANUSCRIPT_ID_COLUMNS = ['base-manuscript-number', 'manuscript-number', 'version-key']
PERSON_ID_COLUMNS = ['person-id']

AUTHORS = pd.DataFrame(
  [],
  columns=MANUSCRIPT_ID_COLUMNS + ['author-person-id'])
PERSONS = pd.DataFrame(
  [],
  columns=PERSON_ID_COLUMNS + ['title', 'first-name', 'middle-name', 'last-name', 'institution'])
MANUSCRIPTS = pd.DataFrame(
  [],
  columns=['manuscript-number'])
MANUSCRIPTS_KEYWORDS = pd.DataFrame(
  [],
  columns=MANUSCRIPT_ID_COLUMNS + ['sequence', 'word'])
MANUSCRIPTS_HISTORY = pd.DataFrame(
  [],
  columns=MANUSCRIPT_ID_COLUMNS + ['stage-affective-person-id', 'stage-name'])

DATASETS = {
  'authors': AUTHORS,
  'persons': PERSONS,
  'persons-current': PERSONS,
  'manuscripts': MANUSCRIPTS,
  'manuscript-keywords': MANUSCRIPTS_KEYWORDS,
  'manuscript-history': MANUSCRIPTS_HISTORY
}

PERSON_ID1 = 'person1'

PERSON1 = {
  'person-id': 'person1',
  'first-name': 'John',
  'last-name': 'Smith'
}

MANUSCRIPT_NO1 = '12345'
MANUSCRIPT_NUMBER1 = 'some-prefix-' + MANUSCRIPT_NO1
VERSION_KEY1 = '11111|0'

MANUSCRIPT_ID_FIELDS1 = {
  'base-manuscript-number': MANUSCRIPT_NUMBER1,
  'manuscript-number': MANUSCRIPT_NUMBER1,
  'version-key': VERSION_KEY1
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

MANUSCRIPT_HISTORY_REVIEW_COMPLETE1 = {
  **MANUSCRIPT_ID_FIELDS1,
  'stage-name': 'Review Complete',
  'stage-affective-person-id': PERSON_ID1
}

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
  datasets['manuscript-keywords'] = pd.DataFrame([
    MANUSCRIPT_KEYWORD1
  ], columns=MANUSCRIPTS_KEYWORDS.columns)
  recommend_reviewers = RecommendReviewers(datasets)
  result = recommend_reviewers.recommend(keywords='', manuscript_no=MANUSCRIPT_NO1)
  assert result == {
    'potential-reviewers': [],
    'matching-manuscripts': [{
      **MANUSCRIPT_ID_FIELDS1,
      'authors': [],
      'reviewers': []
    }]
  }

def test_matching_one_keyword_author():
  datasets = dict(DATASETS)
  datasets['persons-current'] = pd.DataFrame([
    PERSON1
  ], columns=PERSONS.columns)
  datasets['authors'] = pd.DataFrame([
    AUTHOR1
  ], columns=AUTHORS.columns)
  datasets['manuscript-keywords'] = pd.DataFrame([
    MANUSCRIPT_KEYWORD1
  ], columns=MANUSCRIPTS_KEYWORDS.columns)
  recommend_reviewers = RecommendReviewers(datasets)
  result = recommend_reviewers.recommend(keywords=KEYWORD1, manuscript_no='')
  print("result:", result)
  assert result == {
    'potential-reviewers': [{
      'person': PERSON1,
      'author-of-manuscripts': [{
        **MANUSCRIPT_ID_FIELDS1,
        'authors': [PERSON1],
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
  datasets['manuscript-keywords'] = pd.DataFrame([
    MANUSCRIPT_KEYWORD1,
    MANUSCRIPT_KEYWORD1
  ], columns=MANUSCRIPTS_KEYWORDS.columns)
  recommend_reviewers = RecommendReviewers(datasets)
  result = recommend_reviewers.recommend(keywords=KEYWORD1, manuscript_no='')
  print("result:", result)
  assert result == {
    'potential-reviewers': [{
      'person': PERSON1,
      'author-of-manuscripts': [{
        **MANUSCRIPT_ID_FIELDS1,
        'authors': [PERSON1],
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
  datasets['manuscript-history'] = pd.DataFrame([
    MANUSCRIPT_HISTORY_REVIEW_COMPLETE1
  ], columns=MANUSCRIPTS_HISTORY.columns)
  datasets['manuscript-keywords'] = pd.DataFrame([
    MANUSCRIPT_KEYWORD1
  ], columns=MANUSCRIPTS_KEYWORDS.columns)
  recommend_reviewers = RecommendReviewers(datasets)
  result = recommend_reviewers.recommend(keywords=KEYWORD1, manuscript_no='')
  print("result:", result)
  assert result == {
    'potential-reviewers': [{
      'person': PERSON1,
      'author-of-manuscripts': [],
      'reviewer-of-manuscripts': [{
        **MANUSCRIPT_ID_FIELDS1,
        'authors': [],
        'reviewers': [PERSON1]
      }]
    }],
    'matching-manuscripts': []
  }

def test_matching_one_keyword_previous_reviewer_should_return_reviewer_only_once():
  datasets = dict(DATASETS)
  datasets['persons-current'] = pd.DataFrame([
    PERSON1
  ], columns=PERSONS.columns)
  datasets['manuscript-history'] = pd.DataFrame([
    MANUSCRIPT_HISTORY_REVIEW_COMPLETE1,
    MANUSCRIPT_HISTORY_REVIEW_COMPLETE1
  ], columns=MANUSCRIPTS_HISTORY.columns)
  datasets['manuscript-keywords'] = pd.DataFrame([
    MANUSCRIPT_KEYWORD1,
    MANUSCRIPT_KEYWORD1
  ], columns=MANUSCRIPTS_KEYWORDS.columns)
  recommend_reviewers = RecommendReviewers(datasets)
  result = recommend_reviewers.recommend(keywords=KEYWORD1, manuscript_no='')
  print("result:", result)
  assert result == {
    'potential-reviewers': [{
      'person': PERSON1,
      'author-of-manuscripts': [],
      'reviewer-of-manuscripts': [{
        **MANUSCRIPT_ID_FIELDS1,
        'authors': [],
        'reviewers': [PERSON1]
      }]
    }],
    'matching-manuscripts': []
  }
