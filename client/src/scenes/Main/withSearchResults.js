import React from 'react';

import { createSelector } from 'reselect';
import { lifecycle, withProps, renderComponent, compose } from 'recompose';
import debounce from 'debounce';

import { reportError } from '../../monitoring';

import { withDebouncedProp, withPromisedProp, withPromisedPropEnhancer } from '../../components';

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
    abstract: searchOptions.abstract || ''
  }
  if (searchOptions.limit) {
    params.limit = searchOptions.limit;
  }
  if (searchOptions.searchType) {
    params.search_type = searchOptions.searchType;
  }
  return params;
};

export const convertResultsResponse = resultsResponse => resultsResponse && {
  potentialReviewers: resultsResponse['potential_reviewers'],
  relatedManuscriptByVersionId: resultsResponse['related_manuscript_by_version_id'],
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

export const withPushSearchOptions = source => lifecycle({
  componentDidUpdate(prevProps, prevState) {
    if (!prevProps) {
      return;
    }
    const current = source(this.props);
    if (current && (source(prevProps) != current)) {
      this.props.pushSearchOptions(current);
    }
  }
});

const defaultGetSearchOptions = props => props.searchOptions;

export const withSearchResults = (
  WrappedComponent,
  getSearchOptions = defaultGetSearchOptions,
  isDebouncing = null
) => compose(
  withPromisedPropEnhancer(
    props => loadResults(
      props.reviewerRecommendationApi,
      getSearchOptions(props),
      props.authenticationState
    ).then(convertResultsResponse).catch(error => handleErrorResponse(error, props)),
    'searchResults',
    getSearchOptions
  ),

  withPushSearchOptions(props => getSearchOptions(props)),

  withProps(props => {
    if (isDebouncing && isDebouncing(props)) {
      return {
        ...props,
        searchResults: {loading: true}
      }
    }
    return props;
  })
)(WrappedComponent);

export const withDebouncedSearchResults = (
  WrappedComponent,
  getSearchOptions = defaultGetSearchOptions,
  delay = 500
) => withDebouncedProp(
  withSearchResults(
    WrappedComponent,
    props => props.debouncedSearchOptions,
    props => props.debouncingSearch
  ),
  getSearchOptions,
  debouncedSearchOptions => ({ debouncedSearchOptions  }),
  {
    delay,
    debouncingProps: () => ({debouncingSearch: true})
  }
);
