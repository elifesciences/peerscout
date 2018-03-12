import React from 'react';

import { withPromisedProp } from '../../components';

import withAppResolvedPromise from './withAppResolvedPromise';

export const withAllKeywords = WrapperComponent => withPromisedProp(
  WrapperComponent,
  ({ reviewerRecommendationApi }) => reviewerRecommendationApi.getAllKeywords(),
  'allKeywords'
);

export const withLoadedAllKeywords = WrappedComponent => withAllKeywords(
  withAppResolvedPromise(WrappedComponent, 'allKeywords')
);

export default withAllKeywords;
