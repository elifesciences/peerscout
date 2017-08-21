import React from 'react';

import {
  FontAwesomeIcon,
  View,
  Text
} from '../components';

const LoggedInIndicator = ({ auth, style }) => (
  <View style={ style } title={ `Log out as ${auth.email}` } onClick={ () => auth.logout() }>
    <FontAwesomeIcon name="power-off" />
  </View>
);

export default LoggedInIndicator;
