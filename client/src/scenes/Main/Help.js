import React from 'react';

import {
  Link,
  Text,
  View
} from '../../components';

const styles = {
  container: {
    position: 'absolute',
    bottom: 0,
    backgroundColor: '#000',
    color: '#fff',
    opacity: 0.8
  },
  paragraph: {
    margin: 5
  },
  emailLink: {
    marginLeft: 5,
    color: '#ccf',
    textDecoration: 'none'
  }
};

const EmailLink = ({ email }) => (
  <Link
    style={ styles.emailLink }
    target="_blank"
    href={ `mailto:${email}` }
  >
    <Text>{ email }</Text>
  </Link>
);

const Help = props => (
  <View style={ styles.container }>
    <View style={ styles.paragraph }>
      <Text>The numbers on the network chart represent a combined suitability score, based on keywords and abstracts similarity scores, where 100 indicates maximum suitability. You can hover the mouse over the chart to expand it. When clicking on the circles, information on the suggested reviewer will pop up. Such information is also displayed on the right side. The 'Related manuscripts' in the network indicates additional manuscripts that potential reviewers were involved in (as an author). You can also click on those circles to get more details.</Text>
    </View>
    <View style={ styles.paragraph }>
      <Text>On the right, you can see other relevant statistics, such as average review time or availability. That information is shown alongside past manuscripts that the reviewers suggested have been authors or reviewers of.</Text>
    </View>
    <View style={ styles.paragraph }>
      <Text>If you have any questions, please email editorial@elifesciences.org</Text>
      <EmailLink email="editorial@elifesciences.org"/>
    </View>
  </View>
);

export default Help;
