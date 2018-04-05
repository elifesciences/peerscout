import React from 'react';

import {
  ErrorMessage,
  RaisedButton,
  Text,
  View
} from '../../components';

import {
  LazyManuscriptSummary,
  ManuscriptSummary,
  PersonScore,
  PotentialReviewer,
  Score
} from './search-result';

const styles = {
  errorMessage: {
    padding: 20,
    fontSize: 20,
    color: '#f22'
  },
  buttons: {
    padding: 10
  }
};

export const NOT_AUTHORIZED_ERROR_MESSAGE = 'You are not authorized to see the results.';
export const DEFAULT_ERROR_MESSAGE = (
  'This is very unfortunate, but there seems to be some sort of technical issue.' +
  ' Have you tried turning it off and on again?'
);
export const NO_POTENTIAL_REVIEWERS_ERROR_MESSAGE = 'No potential reviewers found';

export const getErrorMessage = error => error && (
  error.notAuthorized ? NOT_AUTHORIZED_ERROR_MESSAGE : DEFAULT_ERROR_MESSAGE
);

export const MANUSCRIPTS_NOT_FOUND_MESSAGE_PREFIX = 'Manuscript not found: ';

export const getManuscriptsNotFoundMessage = manuscriptsNotFound => (
  `${MANUSCRIPTS_NOT_FOUND_MESSAGE_PREFIX}${manuscriptsNotFound.join(', ')}`
);

const extractAllSubjectAreas = manuscripts => {
  const subjectAreas = new Set();
  if (manuscripts) {
    manuscripts.forEach(m => {
      (m['subject_areas'] || []).forEach(subjectArea => {
        subjectAreas.add(subjectArea);
      })
    });
  };
  return subjectAreas;
}

const reviewerPersonId = reviewer => reviewer && reviewer.person && reviewer.person['person_id'];

const SearchResult = ({
  searchResult = {},
  error,
  selectedReviewer,
  selectedManuscript,
  onClearSelection,
  onSelectPotentialReviewer,
  ...otherProps
}) => {
  const {
    potentialReviewers = [],
    relatedManuscriptByVersionId,
    matchingManuscripts = [],
    manuscriptsNotFound,
  } = searchResult;
  const hasManuscriptsNotFound = manuscriptsNotFound && manuscriptsNotFound.length > 0;
  const filteredPotentialReviewers =
    selectedManuscript ? [] : (
      !selectedReviewer ? potentialReviewers :
      potentialReviewers.filter(r => reviewerPersonId(r) === reviewerPersonId(selectedReviewer))
    );
  const nonEmptySelection = selectedReviewer || selectedManuscript;
  const errorMessage = getErrorMessage(error);
  return (
    <View className="result-list">
      {
        errorMessage && (
          <View style={ styles.errorMessage }>
            <ErrorMessage error={ errorMessage } />
          </View>
        )
      }
      {
        hasManuscriptsNotFound && (
          <View style={ styles.errorMessage }>
            <ErrorMessage error={ getManuscriptsNotFoundMessage(manuscriptsNotFound) } />
          </View>
        )
      }
      {
        !nonEmptySelection && matchingManuscripts.map((matchingManuscript, index) => (
          <ManuscriptSummary
            key={ index }
            manuscript={ matchingManuscript }
          />
        ))
      }
      {
        selectedManuscript && (
          <LazyManuscriptSummary
            versionId={ selectedManuscript.version_id }
            { ...otherProps }
          />
        )
      }
      {
        filteredPotentialReviewers.map((potentialReviewer, index) => (
          <PotentialReviewer
            key={ index }
            potentialReviewer={ potentialReviewer }
            relatedManuscriptByVersionId={ relatedManuscriptByVersionId }
            onSelectPotentialReviewer={ onSelectPotentialReviewer }
          />
        ))
      }
      {
        !hasManuscriptsNotFound && !error && potentialReviewers.length === 0 && (
          <View style={ styles.errorMessage }>
            <ErrorMessage error={ NO_POTENTIAL_REVIEWERS_ERROR_MESSAGE } />
          </View>
        )
      }
      {
        nonEmptySelection && (
          <View style={ styles.buttons }>
            <RaisedButton
              primary={ true }
              onClick={ onClearSelection }
              label="Clear Selection"
            />
          </View>
        )
      }
    </View>
  );
};

export default SearchResult;
