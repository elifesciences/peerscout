import React from 'react';

import { createSelector } from 'reselect';
import { lifecycle } from 'recompose';
import debounce from 'debounce';

import { reportError } from '../../monitoring';

import { withDebouncedProp, withPromisedProp } from '../../components';

import { getAuhenticationHeaders } from '../../api'

const shouldSearch = searchOptions => (
  searchOptions.manuscriptNumber ||
  searchOptions.subjectArea ||
  searchOptions.keywords
);

export const convertSearchOptionsToParams = searchOptions => {
  const params = {
    manuscript_no: searchOptions.manuscriptNumber || '',
    subject_area: searchOptions.subjectArea || '',
    keywords: searchOptions.keywords || '',
    abstract: searchOptions.abstract || '',
    limit: searchOptions.limit || '50'
  }
  if (searchOptions.searchType) {
    params.search_type = searchOptions.searchType;
  }
  return params;
};

export const convertResultsResponse = resultsResponse => resultsResponse && {
  potentialReviewers: resultsResponse['potential_reviewers'],
  matchingManuscripts: resultsResponse['matching_manuscripts'],
  manuscriptsNotFound: resultsResponse['manuscripts_not_found'],
  search: resultsResponse['search']
};

const loadResults = (reviewerRecommendationApi, searchOptions, authenticationState) => {
  if (!shouldSearch(searchOptions)) {
    return Promise.resolve();
  }
  return reviewerRecommendationApi.recommendReviewers(
    convertSearchOptionsToParams(searchOptions),
    getAuhenticationHeaders(authenticationState)
  );
};

const handleErrorResponse = (error, props) => {
  reportError("failed to fetch results", error);
  const notAuthorized = props.reviewerRecommendationApi.isNotAuthorizedError(error);
  if (notAuthorized && props.auth) {
    props.auth.revalidateToken();
  }
  throw {
    ...error,
    notAuthorized
  };
}

export const withPushSearchOptions = (WrappedComponent, source) => lifecycle({
  componentDidUpdate(prevProps, prevState) {
    if (!prevProps) {
      return;
    }
    const current = source(this.props);
    if (current && (source(prevProps) != current)) {
      this.props.pushSearchOptions(current);
    }
  }
})(WrappedComponent);

const defaultGetSearchOptions = props => props.searchOptions;

export const withSearchResults = (WrappedComponent, getSearchOptions) => {
  if (!getSearchOptions) {
    getSearchOptions = defaultGetSearchOptions;
  }
  return withPromisedProp(
    withPushSearchOptions(WrappedComponent, props => getSearchOptions(props)),
    props => loadResults(
      props.reviewerRecommendationApi,
      getSearchOptions(props),
      props.authenticationState
    ).then(convertResultsResponse).catch(error => handleErrorResponse(error, props)),
    'searchResults',
    getSearchOptions
  );
};

export const withDebouncedSearchResults = (WrappedComponent, getSearchOptions, delay = 500) => {
  return withDebouncedProp(
    withSearchResults(WrappedComponent, props => props.debouncedSearchOptions),
    getSearchOptions || defaultGetSearchOptions,
    debouncedSearchOptions => ({ debouncedSearchOptions  }),
    delay
  );
};
