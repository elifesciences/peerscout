import React from 'react';

import {
  reportError
} from '../../monitoring';

import AppLoading from './AppLoading';
import AppError from './AppError';

const styles = {
  appLoading: {
    flex: 1,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center'
  }
}

const withAppLoadingIndicator = (
  WrappedComponent, isLoading, getError, loadingStyle = styles.appLoading
) => props => {
  if (isLoading(props)) {
    return <AppLoading style={ loadingStyle }/>;
  }
  const error = getError && getError(props);
  if (error) {
    reportError(error, error);
    return <AppError {...props} error={ error } />;
  }
return <WrappedComponent {...props} />;
};

export default withAppLoadingIndicator;
