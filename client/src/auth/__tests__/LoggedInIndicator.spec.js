import React from 'react';

import test from 'tape';
import { shallow } from 'enzyme';

import LoggedInIndicator from '../LoggedInIndicator';

const EMAIL = 'test@x.org';
const AUTH = {email: EMAIL};
const NOT_LOGGED_IN_AUTH = {email: null};

test('LoggedInIndicator', g => {
  g.test('.should be defined', t => {
    t.true(LoggedInIndicator);
    t.end();
  });

  g.test('.should show email in title', t => {
    const component = shallow(<LoggedInIndicator auth={ AUTH } />);
    const title = component.props()['title'];
    t.true(title.indexOf(EMAIL) >= 0, `title "${title}" should contain email "${EMAIL}"`);
    t.end();
  });

  g.test('.should not render if not logged in', t => {
    const component = shallow(<LoggedInIndicator auth={ NOT_LOGGED_IN_AUTH } />);
    t.equal(component.get(0), null);
    t.end();
  });
});
