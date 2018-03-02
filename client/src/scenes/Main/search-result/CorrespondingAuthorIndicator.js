import React from 'react';

import {
  FontAwesomeIcon,
  Link,
  View
} from '../../../components';

import { commonStyles } from '../../../styles';

const styles = {
  correspondingAuthorIndicator: {
    ...commonStyles.link,
    display: 'inline-block',
    marginLeft: 5
  }
};

const CorrespondingAuthorIndicator = ({ person: { email } }) => {
  if (email) {
    return (
      <Link
        style={ styles.correspondingAuthorIndicator }
        target="_blank"
        href={ `mailto:${email}` }
        title={ email }
      >
        <FontAwesomeIcon name="envelope"/>
      </Link>
    );
  } else {
    return (
      <View style={ styles.correspondingAuthorIndicator }>
        <FontAwesomeIcon name="envelope"/>
      </View>
    );
  }
};

export default CorrespondingAuthorIndicator;
