import React from 'react';

import { withPromisedProp } from '../../components';

import withAppResolvedPromise from './withAppResolvedPromise';

export const withAllSubjectAreas = WrapperComponent => withPromisedProp(
  WrapperComponent,
  ({ reviewerRecommendationApi }) => reviewerRecommendationApi.getAllSubjectAreas(),
  'allSubjectAreas'
);

export const withLoadedAllSubjectAreas = WrappedComponent => withAllSubjectAreas(
  withAppResolvedPromise(WrappedComponent, 'allSubjectAreas')
);

export default withAllSubjectAreas;
