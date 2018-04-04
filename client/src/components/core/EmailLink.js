import React from 'react';

import {
  FlatButton,
  FontAwesomeIcon,
  Link,
  Text,
  View
} from '../../components';

const styles = {
  emailLink: {
    textDecoration: 'none'
  }
};

export const EmailLink = ({ email, style }) => (
  <Link
    style={ style || styles.emailLink }
    target="_blank"
    href={ `mailto:${email}` }
  >
    <Text>{ email }</Text>
  </Link>
);

export default EmailLink;
