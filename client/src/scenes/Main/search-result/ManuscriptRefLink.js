import React from 'react';

import {
  InlineContainer,
  Link,
  Text,
  TooltipWrapper,
  View
} from '../../../components';

import {
  formatManuscriptDoi,
  doiUrl
} from '../formatUtils';

import { commonStyles } from '../../../styles';

const styles = {
  manuscriptLink: {
    ...commonStyles.link
  }
};

export const ManuscriptRefLink = ({ manuscript }) => (
  <Link
    style={ styles.manuscriptLink }
    target="_blank"
    href={ doiUrl(manuscript['doi']) }
  >
    <Text>{ formatManuscriptDoi(manuscript) }</Text>
  </Link>
);

export default ManuscriptRefLink;
