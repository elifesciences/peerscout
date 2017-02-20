import React from 'react';

const styles = {
  container: {
    display: 'none'
  }
};

const Comment = ({ text, children, ...otherProps }) => (
  <span {...otherProps} style={ styles.container }>
    { text }
    { children }
  </span>
);

export default Comment;
