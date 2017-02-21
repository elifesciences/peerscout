import React from 'react';

import View from './View';

const styles = {
  flexRow: {
    display: 'flex',
    flexDirection: 'row'
  }
};

const FlexRow = props => (
  <View style={ styles.flexRow }>
    { props.children }
  </View>
);

export default FlexRow;
