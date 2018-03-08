import React from 'react';

import { withPromisedProp } from '../../components';

import withResolvedPromise from './withResolvedPromise';

export const withAllKeywords = WrapperComponent => withPromisedProp(
  WrapperComponent,
  ({ reviewerRecommendationApi }) => reviewerRecommendationApi.getAllKeywords(),
  'allKeywords'
);

export const withLoadedAllKeywords = WrappedComponent => withAllKeywords(
  withResolvedPromise(WrappedComponent, 'allKeywords')
);

export default withAllKeywords;
