import React from 'react';

import View from './View';

const styles = {
  flexColumn: {
    display: 'flex',
    flexDirection: 'column'
  }
};

const FlexColumn = props => (
  <View style={ Object.assign({}, styles.flexColumn, props.style) }>
    { props.children }
  </View>
);

export default FlexColumn;
