import React from 'react';

import { NOT_AUTHORIZED_ERROR } from '../../api';

import {
  FlexColumn,
  View,
  Text,
  EmailLink,
  ErrorMessage
} from '../../components';

import {
  LoggedInIndicator,
} from '../../auth';

const styles = {
  loggedInIndicator: {
    position: 'absolute',
    top: 0,
    right: 0,
    zIndex: 10,
    padding: 5,
    color: '#000'
  },
  error: {
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: 30,
    margin: 50
  }
};

const NotAuthorizedErrorMessage = props => (
  <View>
    <Text>It seems that this address is not authorised.
    Please ensure you are using the email address registered with eLife.
    If the problems persist, please contact us at</Text>
    <Text>{ ' ' }</Text>
    <EmailLink email="editorial@elifesciences.org"/>
  </View>
);

export const AppErrorMessage = ({ error }) => {
  if (error == NOT_AUTHORIZED_ERROR) {
    return (<NotAuthorizedErrorMessage/>);
  }
  return (<ErrorMessage error={ error } />);
};

export const AppError = ({error, style, auth, ...props}) => (
  <View style={ style || styles.error }>
    <LoggedInIndicator auth={ auth } style={ styles.loggedInIndicator }/>
    <AppErrorMessage error={ error } />
  </View>
);

export default AppError;
