import React from 'react';

import {
  FlexColumn,
  FlexRow,
  LoadingIndicator,
  View
} from '../components';

import LoginForm from './LoginForm';

const styles = {
  loginForm: {
    flex: 1,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center'
  },
  loadingIndicator: {
    position: 'absolute',
    marginTop: 10,
    marginLeft: 10
  }
}

const withLoginForm = (
  WrappedComponent
) => props => {
  const { authenticationState, auth } = props;
  if (authenticationState.authenticating) {
    return (
      <LoadingIndicator style={ styles.loadingIndicator } loading={ true } />
    );
  }
  if (!authenticationState.authenticated) {
    return (
      <LoginForm auth={ auth } style={ styles.loginForm }/>
    );
  }
  return <WrappedComponent {...props} />;
};

export default withLoginForm;
