import React from 'react';

import {
  RaisedButton,
  Text,
  View
} from '../../components';

import {
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
  searchResult,
  selectedReviewer,
  selectedManuscript,
  onClearSelection,
  onSelectPotentialReviewer
}) => {
  const {
    potentialReviewers = [],
    matchingManuscripts = [],
    manuscriptsNotFound,
    notAuthorized,
    error
  } = searchResult;
  const requestedSubjectAreas = extractAllSubjectAreas(matchingManuscripts);
  const hasManuscriptsNotFound = manuscriptsNotFound && manuscriptsNotFound.length > 0;
  const filteredPotentialReviewers =
    selectedManuscript ? [] : (
      !selectedReviewer ? potentialReviewers :
      potentialReviewers.filter(r => reviewerPersonId(r) === reviewerPersonId(selectedReviewer))
    );
  const nonEmptySelection = selectedReviewer || selectedManuscript;
  const errorMessage = error && (
    notAuthorized ? 'You are not authorized to see the results.' :
    'This is very unfortunate, but there seems to be some sort of technical issue. Have you tried turning it off and on again?'
  );
  return (
    <View className="result-list">
      {
        errorMessage && (
          <View style={ styles.errorMessage }>
            <Text>
              { errorMessage }
            </Text>
          </View>
        )
      }
      {
        hasManuscriptsNotFound && (
          <View style={ styles.errorMessage }>
            <Text>{ `Manuscript not found: ${manuscriptsNotFound.join(', ')}` }</Text>
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
          <ManuscriptSummary
            manuscript={ selectedManuscript }
          />
        )
      }
      {
        filteredPotentialReviewers.map((potentialReviewer, index) => (
          <PotentialReviewer
            key={ index }
            potentialReviewer={ potentialReviewer }
            requestedSubjectAreas={ requestedSubjectAreas }
            onSelectPotentialReviewer={ onSelectPotentialReviewer }
          />
        ))
      }
      {
        !hasManuscriptsNotFound && !error && potentialReviewers.length === 0 && (
          <View style={ styles.errorMessage }>
            <Text>{ 'No potential reviewers found' }</Text>
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
