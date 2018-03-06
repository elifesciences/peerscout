import React from 'react';

import {
  FontAwesomeIcon,
  Link,
  Text
} from '../../../components';

import { commonStyles } from '../../../styles';

import { personFullName } from '../formatUtils';

const styles = {
  membershipLink: {
    ...commonStyles.link,
    display: 'inline-block',
    marginLeft: 10
  }
};

export const personWebSearchUrl = person => (
  `http://search.crossref.org/?q=${encodeURIComponent(personFullName(person))}`
);

const PersonWebSearchLink = ({ person }) => (
  <Link
    style={ styles.membershipLink }
    target="_blank"
    href={ personWebSearchUrl(person) }
  >
    <Text><FontAwesomeIcon name="search"/></Text>
  </Link>
);

export default PersonWebSearchLink;
