import React from 'react';

import {
  View,
  Text,
  FlexColumn,
  RaisedButton,
  FontAwesomeIcon
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

const LoginForm = ({ auth, style }) => (
  <View style={ style }>
    <FlexColumn>
      <RaisedButton
        onClick={ () => auth.loginUsingMagicLink() }
        primary={ true }
        label="Login using Magic Link"
        icon={ <FontAwesomeIcon style={ styles.icon } name="sign-in"/> }
      />
      {
        auth.error_description && (
          <Text style={ styles.error }>{ auth.error_description }</Text>
        )
      }
    </FlexColumn>
  </View>
);

export default LoginForm;
