import React from 'react';

import {
  FontAwesomeIcon
} from '../icons';

import {
  View
} from '../core';

const LoadingIndicator = props => {
  if (props.loading) {
    return (
      <FontAwesomeIcon name="spinner fa-spin"/>
    );
  }
  return props.children[0] || props.children;
};

export default LoadingIndicator;
