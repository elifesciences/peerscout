import React from 'react';

import test from 'tape';
import { shallow } from 'enzyme';

import CorrespondingAuthorIndicator from '../CorrespondingAuthorIndicator';

const EMAIL = 'person@test.com';

const PERSON = {
  email: EMAIL
};

test('CorrespondingAuthorIndicator', g => {
  g.test('.should be defined', t => {
    t.true(CorrespondingAuthorIndicator);
    t.end();
  });

  g.test('.should render email link if person has email', t => {
    const person = {...PERSON, email: EMAIL};
    const component = shallow(<CorrespondingAuthorIndicator person={ person } />);
    const linkComponent = component.find('Link');
    t.equal(linkComponent.props()['href'], `mailto:${EMAIL}`);
    t.end();
  });

  g.test('.should not render email link if person has no email', t => {
    const person = {...PERSON, email: null};
    const component = shallow(<CorrespondingAuthorIndicator person={ person } />);
    const linkComponent = component.find('Link');
    t.equal(linkComponent.length, 0);
    t.end();
  });
});
