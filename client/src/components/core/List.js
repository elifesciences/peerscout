import React from 'react';

const List = props => (
  <ul { ...props }>
    { props.children }
  </ul>
);

export default List;
