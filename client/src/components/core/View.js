import React from 'react';
import Radium from 'radium';

const View = props => (
  <div { ...props }>
    { props.children }
  </div>
);

export default Radium(View);
