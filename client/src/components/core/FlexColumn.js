import React from 'react';

import View from './View';

const styles = {
  flexColumn: {
    display: 'flex',
    flexDirection: 'column'
  }
};

const FlexColumn = props => (
  <View style={ styles.flexColumn }>
    { props.children }
  </View>
);

export default FlexColumn;
