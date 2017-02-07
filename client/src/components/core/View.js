import React from 'react';

const View = props => (
  <div { ...props }>
    { props.children }
  </div>
);

export default View;
