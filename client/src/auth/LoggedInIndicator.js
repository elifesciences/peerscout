import React from 'react';

import {
  FontAwesomeIcon,
  View,
  Text
} from '../components';

const LoggedInIndicator = ({ auth, style }) => ((auth && auth.email) && (
  <View style={ style } title={ `Log out as ${auth.email}` } onClick={ () => auth.logout() }>
    <FontAwesomeIcon name="power-off" />
  </View>
)) || null;

export default LoggedInIndicator;
