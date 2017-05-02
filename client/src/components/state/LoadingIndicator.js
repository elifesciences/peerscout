import React from 'react';

import {
  FontAwesomeIcon
} from '../icons';

const LoadingIndicator = props => {
  if (props.loading) {
    return (
      <FontAwesomeIcon style={ props.style } name="spinner fa-spin"/>
    );
  }
  return props.children[0] || props.children;
};

export default LoadingIndicator;
