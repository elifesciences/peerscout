import React from 'react';

import {
  FontAwesomeIcon,
  View,
  Text
} from '../components';

const LoggedInIndicator = ({ auth, style }) => {
  const authenticationState = auth && auth.getAuthenticationState();
  const email = authenticationState && authenticationState.email;
  if (email) {
    return (
      <View
        style={ style }
        title={ `Log out as ${email}` }
        onClick={ () => auth.logout() }
      >
        <FontAwesomeIcon name="power-off" />
      </View>
    );
  }
  return null;
};

export default LoggedInIndicator;
