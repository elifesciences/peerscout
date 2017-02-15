import React from 'react';

const HeaderTitle = ({ children, ...otherProps }) => (
  <h3 {...otherProps }>
    { children }
  </h3>
);

export default HeaderTitle;
