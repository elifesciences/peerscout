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

def test_no_match():
  recommend_reviewers = RecommendReviewers(DATASETS)
  result = recommend_reviewers.recommend(keywords='', manuscript_no='')
  assert result == {
    'potential-reviewers': [],
    'matching-manuscripts': []
  }
