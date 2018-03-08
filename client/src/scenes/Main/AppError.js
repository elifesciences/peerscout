import React from 'react';

import {
  View,
  ErrorMessage
} from '../../components';

const styles = {
  error: {
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: 30
  }
};

export const AppError = ({error, style, ...props}) => (
  <View { ...props } style={ style || styles.error }>
    <ErrorMessage error={ error } />
  </View>
);

export default AppError;
