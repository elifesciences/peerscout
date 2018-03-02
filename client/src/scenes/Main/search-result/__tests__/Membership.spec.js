import React from 'react';

import test from 'tape';
import { shallow, render } from 'enzyme';

import Membership from '../Membership';
import {
  OrcidLink,
  CrossrefOrcidSearchLink,
  UnrecognisedMembership,
  orcidUrl,
  crossrefOrcidSearchUrl
} from '../Membership';

const ORCID_1 = '12345';
const ORCID_MEMBERSHIP = {member_type: 'ORCID', member_id: ORCID_1};
const OTHER_MEMBERSHIP = {member_type: 'OTHER', member_id: 'other1'};

test('Membership', g => {
  g.test('.should be defined', t => {
    t.true(Membership);
    t.end();
  });

  g.test('.should render orcid link', t => {
    const component = shallow(<Membership membership={ ORCID_MEMBERSHIP } />);
    const linkComponent = component.find('OrcidLink');
    t.equal(linkComponent.props()['orcid'], ORCID_MEMBERSHIP.member_id);
    t.end();
  });

  g.test('.should render crossref orcid search link', t => {
    const component = shallow(<Membership membership={ ORCID_MEMBERSHIP } />);
    const linkComponent = component.find('CrossrefOrcidSearchLink');
    t.equal(linkComponent.props()['orcid'], ORCID_MEMBERSHIP.member_id);
    t.end();
  });

  g.test('.should render unrecognised membership', t => {
    const component = shallow(<Membership membership={ OTHER_MEMBERSHIP } />);
    const subComponent = component.find('UnrecognisedMembership');
    t.equal(subComponent.props()['membership'], OTHER_MEMBERSHIP);
    t.end();
  });
});

test('Membership.OrcidLink', g => {
  g.test('.should be defined', t => {
    t.true(OrcidLink);
    t.end();
  });

  g.test('.should render link', t => {
    const component = shallow(<OrcidLink orcid={ ORCID_1 } />);
    const linkComponent = component.find('Link');
    t.equal(linkComponent.props()['href'], orcidUrl(ORCID_1));
    t.end();
  });
});

test('Membership.CrossrefOrcidSearchLink', g => {
  g.test('.should be defined', t => {
    t.true(CrossrefOrcidSearchLink);
    t.end();
  });

  g.test('.should render link', t => {
    const component = shallow(<CrossrefOrcidSearchLink orcid={ ORCID_1 } />);
    const linkComponent = component.find('Link');
    t.equal(linkComponent.props()['href'], crossrefOrcidSearchUrl(ORCID_1));
    t.end();
  });
});

test('Membership.UnrecognisedMembership', g => {
  g.test('.should be defined', t => {
    t.true(UnrecognisedMembership);
    t.end();
  });

  g.test('.should render member type', t => {
    const component = render(<UnrecognisedMembership membership={ OTHER_MEMBERSHIP } />);
    const text = component.text();
    t.true(text.indexOf(OTHER_MEMBERSHIP.member_type) >= 0);
    t.end();
  });
});
