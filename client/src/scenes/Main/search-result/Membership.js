import React from 'react';

import {
  Link,
  Text,
  View
} from '../../../components';

import { commonStyles } from '../../../styles';

const styles = {
  inlineContainer: {
    display: 'inline-block'
  },
  membershipLink: {
    ...commonStyles.link,
    display: 'inline-block',
    marginLeft: 10
  },
  unrecognisedMembership: {
    display: 'inline-block',
    marginLeft: 10
  }
};

export const orcidUrl = orcid => `http://orcid.org/${orcid}`;
export const crossrefOrcidSearchUrl = orcid => `http://search.crossref.org/?q=${orcid}`;

export const OrcidLink = ({ orcid, style }) => (
  <Link style={ style } target="_blank" href={ orcidUrl(orcid) }>
    <Text>ORCID</Text>
  </Link>
);

export const CrossrefOrcidSearchLink = ({ orcid, style }) => (
  <Link style={ style } target="_blank" href={ crossrefOrcidSearchUrl(orcid) }>
    <Text>Crossref</Text>
  </Link>
);

export const UnrecognisedMembership = ({ membership }) => (
  <Text style={ styles.unrecognisedMembership }>
    { `${membership.member_type}: ${membership.member_id}` }
  </Text>
);

const Membership = ({ membership }) => {
  if (membership['member_type'] != 'ORCID') {
    return <UnrecognisedMembership membership={ membership } />
  }
  const orcid = membership.member_id;
  return (
    <View style={ styles.inlineContainer }>
      <OrcidLink style={ styles.membershipLink } orcid={ orcid } />
      <CrossrefOrcidSearchLink style={ styles.membershipLink } orcid={ orcid } />
    </View>
  );
};

export default Membership;
