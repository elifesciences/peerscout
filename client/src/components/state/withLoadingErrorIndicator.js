import React from 'react';

import { branch, renderComponent, mapProps, compose } from 'recompose';

import DefaultLoadingIndicator from './LoadingIndicator';
import DefaultErrorMessage from './ErrorMessage';

const renderLoadingIndicator = LoadingIndicator => (
  renderComponent(mapProps(props => ({loading: true}))(LoadingIndicator))
);

const renderErrorMessage = (ErrorMessage, getError) => renderComponent(mapProps(props => ({
  error: getError(props)
}))(ErrorMessage));

export const withLoadingIndicator = (isLoading, LoadingIndicator = DefaultLoadingIndicator) => (
  branch(
    isLoading,
    renderLoadingIndicator(LoadingIndicator)
  )
);

export const withErrorMessage = (getError, ErrorMessage = DefaultErrorMessage) => (
  branch(
    getError,
    renderErrorMessage(ErrorMessage, getError)
  )
);

export const withLoadingErrorIndicator = ({
  isLoading,
  getError,
  LoadingIndicator = DefaultLoadingIndicator,
  ErrorMessage = DefaultErrorMessage
}) => compose(
  withLoadingIndicator(isLoading, LoadingIndicator),
  withErrorMessage(getError, ErrorMessage)
);
