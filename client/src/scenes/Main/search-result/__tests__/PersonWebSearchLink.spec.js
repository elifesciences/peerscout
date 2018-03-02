import React from 'react';

import test from 'tape';
import { shallow, render } from 'enzyme';

import PersonWebSearchLink from '../PersonWebSearchLink';
import { personWebSearchUrl } from '../PersonWebSearchLink';

const PERSON = {
  first_name: 'John',
  last_name: 'Doh'
};

test('PersonWebSearchLink', g => {
  g.test('.should be defined', t => {
    t.true(PersonWebSearchLink);
    t.end();
  });

  g.test('.should render email', t => {
    const component = shallow(<PersonWebSearchLink person={ PERSON } />);
    t.equal(component.props()['href'], personWebSearchUrl(PERSON));
    t.end();
  });
});
