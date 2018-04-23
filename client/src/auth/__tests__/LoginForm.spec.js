import React from 'react';

import test from 'tape';
import { shallow } from 'enzyme';

import LoginForm from '../LoginForm';

const asAuth = authenticationState => ({
  getAuthenticationState: () => authenticationState
});

const ERROR = 'error message 1';

const NO_ERROR_AUTH = asAuth({error_description: null});
const ERROR_AUTH = asAuth({error_description: ERROR});

test('LoginForm', g => {
  g.test('.should be defined', t => {
    t.true(LoginForm);
    t.end();
  });

  g.test('.should show error message if defined', t => {
    const component = shallow(<LoginForm auth={ ERROR_AUTH } />);
    const errorMessageComponent = component.find('ErrorMessage');
    t.equal(errorMessageComponent.length, 1);
    t.true(errorMessageComponent.props()['error'], ERROR);
    t.end();
  });

  g.test('.should not show error message if not defined', t => {
    const component = shallow(<LoginForm auth={ NO_ERROR_AUTH } />);
    const errorMessageComponent = component.find('ErrorMessage');
    t.equal(errorMessageComponent.length, 0);
    t.end();
  });
});
