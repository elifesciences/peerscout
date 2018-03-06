import React from 'react';

import test from 'tape';
import { shallow, render } from 'enzyme';

import PersonEmailLink from '../PersonEmailLink';
import { emailLinkUrl } from '../PersonEmailLink';

const EMAIL = 'person@test.com';

const PERSON = {
  email: EMAIL
};

test('PersonEmailLink', g => {
  g.test('.should be defined', t => {
    t.true(PersonEmailLink);
    t.end();
  });

  g.test('.should render email', t => {
    const component = render(<PersonEmailLink person={ PERSON } />);
    t.equal(component.text(), EMAIL);
    t.end();
  });

  g.test('.should add href', t => {
    const component = shallow(<PersonEmailLink person={ PERSON } />);
    t.equal(component.props()['href'], emailLinkUrl(EMAIL));
    t.end();
  });
});
