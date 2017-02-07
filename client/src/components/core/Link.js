import React from 'react';

const Link = props => (
  <a { ...props }>
    { props.children }
  </a>
);

export default Link;
