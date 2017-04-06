import React from 'react';

import {
  HeaderTitle,
  Text,
  View
} from '../../components';

const styles = {
  header: {
    margin: 0
  },
  label: {
    fontWeight: 'bold'
  },
  abstract: {
    marginTop: 5
  }
};


const ManuscriptTooltipContent = ({
  manuscript: { title, abstract, 'subject_areas': subjectAreas }
}) => (
  <View>
    <HeaderTitle style={ styles.header }>{ title }</HeaderTitle>
    <View>
      <Text style={ styles.label }>{ 'Subject Areas: ' }</Text>
      <Text>{ subjectAreas.join(', ')}</Text>
    </View>
    <View style={ styles.abstract }>
      <Text>{ abstract }</Text>
    </View>
  </View>
);

export default ManuscriptTooltipContent;
