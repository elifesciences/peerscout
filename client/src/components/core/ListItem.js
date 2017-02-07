import React from 'react';

const ListItem = props => (
  <li { ...props }>
    { props.children }
  </li>
);

export default ListItem;
