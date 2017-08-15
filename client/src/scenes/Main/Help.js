import React from 'react';

import {
  FlatButton,
  FontAwesomeIcon,
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
  },
  closeButton: {
    container: {
      color: '#fff',
      float: 'right',
      minWidth: 40
    },
    labelStyle: {
      color: '#fff'
    }
  },
  openButton: {
    container: {
      color: '#fff',
      minWidth: 35
    },
    labelStyle: {
      color: '#fff'
    }
  },
  containerVisible: {
  },
  containerHidden: {
    display: 'none'
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

const CloseButton = ({ onClick }) => (
  <FlatButton
    style={ styles.closeButton.container }
    labelStyle={ styles.closeButton.labelStyle }
    onClick={ onClick }
  >
    <FontAwesomeIcon name="window-close-o"/>
  </FlatButton>
);

const OpenButton = ({ onClick }) => (
  <FlatButton
    style={ styles.openButton.container }
    labelStyle={ styles.openButton.labelStyle }
    onClick={ onClick }
  >
    <FontAwesomeIcon name="question"/>
  </FlatButton>
);

const HelpContents = props => (
  <View>
    <View style={ styles.paragraph }>
      <Text>Please search by Manuscript (5 digits) or by Criteria (these are mutually exclusive).</Text>
    </View>
    <View style={ styles.paragraph }>
      <Text>The numbers on the network chart represent a combined suitability score, based on keywords and abstracts similarity scores, where 100 indicates maximum suitability. You can hover the mouse over the chart to expand it. When clicking on the circles, information on the suggested reviewer will pop up. Such information is also displayed on the right side. The 'Related manuscripts' in the network indicates additional manuscripts that potential reviewers were involved in (as an author). You can also click on those circles to get more details.</Text>
    </View>
    <View style={ styles.paragraph }>
      <Text>On the right, you can see other relevant statistics, such as average review time or availability. That information is shown alongside past manuscripts that the reviewers suggested have been authors or reviewers of. The dark grey background colouring in the list of authors indicate the corresponding author of the manuscript.
        Although other browsers work, Chrome has a better performance.</Text>
    </View>
    <View style={ styles.paragraph }>
      <Text>If you have any questions, please email</Text>
      <EmailLink email="editorial@elifesciences.org"/>
    </View>
  </View>
);

const Help = ({ open, onClose, onOpen }) => (
  <View style={ styles.container }>
    <View style={ open ? styles.containerVisible : styles.containerHidden }>
      <CloseButton onClick={ onClose }/>
      <HelpContents/>
    </View>
    <View style={ !open ? styles.containerVisible : styles.containerHidden }>
      <OpenButton onClick={ onOpen }/>
    </View>
  </View>
);

export default Help;
