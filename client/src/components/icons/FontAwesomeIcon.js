import React from 'react';

const FontAwesomeIcon = props => {
  const className = `fa fa-${props.name}`;
  return (
    <i className={ className } aria-hidden="true" style={ props.style }></i>
  );
};

export default FontAwesomeIcon;
