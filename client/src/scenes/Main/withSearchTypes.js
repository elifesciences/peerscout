import React from 'react';

import { withPromisedProp } from '../../components';

import { getAuhenticationHeaders } from '../../api'

import withAppResolvedPromise from './withAppResolvedPromise';

export const withSearchTypes = WrapperComponent => withPromisedProp(
  WrapperComponent,
  ({ reviewerRecommendationApi, authenticationState }) => reviewerRecommendationApi.getSearchTypes(
    getAuhenticationHeaders(authenticationState)
  ),
  'searchTypes'
);

export const withLoadedSearchTypes = WrappedComponent => withSearchTypes(
  withAppResolvedPromise(WrappedComponent, 'searchTypes')
);

export default withSearchTypes;
