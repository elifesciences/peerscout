import React from 'react';

import { renderComponent } from 'recompose';

import { withPromisedProp, withResolvedPromise } from '../../../components';
import { getAuhenticationHeaders } from '../../../api'

import { ManuscriptSummary } from './ManuscriptSummary';

export const withPromisedManuscriptVersion = WrappedComponent => (
  withPromisedProp(
    withResolvedPromise('manuscript')(WrappedComponent),
    props => props.reviewerRecommendationApi.getManuscriptVersion(
      props.versionId,
      getAuhenticationHeaders(props.authenticationState)
    ),
    'manuscript',
    props => props.versionId
  )
);

const _LazyManuscriptSummary = withPromisedManuscriptVersion(ManuscriptSummary);

export const LazyManuscriptSummary = props => <_LazyManuscriptSummary { ...props } />;
