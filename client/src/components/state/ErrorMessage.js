import React from 'react';

import {
  Text
} from '../../components';

const styles = {
  error: {
    color: 'red'
  }
};

export const UNKNOWN_ERROR = 'An unexpected error happened, please try again later';

export const ERROR_CODE_PREFIX = 'Error: ';

export const getErrorMessage = error => {
  let errorMessage = error;
  if (typeof(error) == 'object') {
    errorMessage = error.error || error.errorMessage;
  }
  if (typeof(errorMessage) == 'number') {
    errorMessage = ERROR_CODE_PREFIX + errorMessage;
  }
  return errorMessage || UNKNOWN_ERROR
};

export const ErrorMessage = ({error, style, ...props}) => (
  <Text { ...props } style={ style || styles.error }>{ getErrorMessage(error) }</Text>
);

export default ErrorMessage;
