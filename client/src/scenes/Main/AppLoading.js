import React from 'react';

import {
  LoadingIndicator,
  View
} from '../../components';

const styles = {
  loadingIndicator: {
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: 150
  }
};

const AppLoading = props => (
  <View { ...props }>
    <LoadingIndicator style={ styles.loadingIndicator } loading={ true }/>
  </View>
);

export default AppLoading;
