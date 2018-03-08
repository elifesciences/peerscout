import React from 'react';

import { withPromisedProp } from '../../components';

import { getAuhenticationHeaders } from '../../api'

import withResolvedPromise from './withResolvedPromise';

export const withSearchTypes = WrapperComponent => withPromisedProp(
  WrapperComponent,
  ({ reviewerRecommendationApi, authenticationState }) => reviewerRecommendationApi.getSearchTypes(
    getAuhenticationHeaders(authenticationState)
  ),
  'searchTypes'
);

export const withLoadedSearchTypes = WrappedComponent => withSearchTypes(
  withResolvedPromise(WrappedComponent, 'searchTypes')
);

export default withSearchTypes;
