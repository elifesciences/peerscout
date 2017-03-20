import React from 'react';
import View from './View';

const styles = {
  inlineContainer: {
    display: 'inline-block'
  }
}

const InlineContainer = props => (
  <View style={ styles.inlineContainer }>
    { props.children }
  </View>
);

export default InlineContainer;
