import React from 'react';

import {
  View,
  Text,
  FlexColumn,
  RaisedButton,
  FontAwesomeIcon,
  ErrorMessage
} from '../components';

const styles = {
  icon: {
    color: '#fff'
  },
  error: {
    marginTop: 10,
    color: 'red'
  }
};

const LoginForm = ({ auth, style }) => {
  const error = auth.getAuthenticationState().error_description;
  return (
    <View style={ style }>
      <FlexColumn>
        <RaisedButton
          onClick={ () => auth.loginUsingMagicLink() }
          primary={ true }
          label="Login using Magic Link"
          icon={ <FontAwesomeIcon style={ styles.icon } name="sign-in"/> }
        />
        {
          error && (
            <ErrorMessage style={ styles.error } error={ error } />
          )
        }
      </FlexColumn>
    </View>
  );
};

export default LoginForm;
