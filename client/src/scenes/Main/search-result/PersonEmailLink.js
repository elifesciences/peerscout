import React from 'react';

import {
  Link,
  Text
} from '../../../components';

import { commonStyles } from '../../../styles';

const styles = {
  emailLink: {
    ...commonStyles.link,
    display: 'inline-block',
    marginLeft: 10
  },
};

export const emailLinkUrl = email => `mailto:${email}`;

const PersonEmailLink = ({ person: { email } }) => (
  <Link
    style={ styles.emailLink }
    target="_blank"
    href={ emailLinkUrl(email) }
  >
    <Text>{ email }</Text>
  </Link>
);

export default PersonEmailLink;
