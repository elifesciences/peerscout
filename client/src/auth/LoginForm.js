import React from 'react';

import {
  View,
  RaisedButton,
  FontAwesomeIcon
} from '../components';

const styles = {
  icon: {
    color: '#fff'
  }
};

const LoginForm = ({ auth, style }) => (
  <View style={ style }>
    <RaisedButton
      onClick={ () => auth.loginUsingMagicLink() }
      primary={ true }
      label="Login using Magic Link"
      icon={ <FontAwesomeIcon style={ styles.icon } name="sign-in"/> }
    />
  </View>
);

export default LoginForm;
