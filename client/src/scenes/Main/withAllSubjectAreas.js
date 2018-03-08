import React from 'react';

import { withPromisedProp } from '../../components';

import withResolvedPromise from './withResolvedPromise';

export const withAllSubjectAreas = WrapperComponent => withPromisedProp(
  WrapperComponent,
  ({ reviewerRecommendationApi }) => reviewerRecommendationApi.getAllSubjectAreas(),
  'allSubjectAreas'
);

export const withLoadedAllSubjectAreas = WrappedComponent => withAllSubjectAreas(
  withResolvedPromise(WrappedComponent, 'allSubjectAreas')
);

export default withAllSubjectAreas;
