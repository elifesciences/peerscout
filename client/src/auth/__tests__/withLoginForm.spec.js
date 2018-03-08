import React from 'react';

import test from 'tape';
import { shallow } from 'enzyme';

import withLoginForm from '../withLoginForm';

const WrappedComponent = props => (<div></div>);

const NOT_AUTHENTICATED = {
  authenticating: false,
  authenticated: false
};

const AUTHENTICATING = {
  authenticating: true,
  authenticated: false
};

const AUTHENTICATED = {
  authenticating: false,
  authenticated: true
};

test('withLoginForm', g => {
  g.test('.should be defined', t => {
    t.true(withLoginForm);
    t.end();
  });

  g.test('.should render wrapped component and pass custom prop to wrapped component if authenticated', t => {
    const Component = withLoginForm(WrappedComponent);
    const component = shallow(<Component other="123" authenticationState={ AUTHENTICATED } />);
    const wrappedComponent = component.find('WrappedComponent');
    t.equal(wrappedComponent.props()['other'], '123');
    t.end();
  });

  g.test('.should render LoginForm if not authenticated', t => {
    const Component = withLoginForm(WrappedComponent);
    const component = shallow(<Component other="123" authenticationState={ NOT_AUTHENTICATED } />);
    t.equal(component.find('LoginForm').length, 1);
    t.equal(component.find('WrappedComponent').length, 0);
    t.end();
  });

  g.test('.should render LoadingIndicator if not authenticated', t => {
    const Component = withLoginForm(WrappedComponent);
    const component = shallow(<Component other="123" authenticationState={ AUTHENTICATING } />);
    t.equal(component.find('LoadingIndicator').length, 1);
    t.equal(component.find('WrappedComponent').length, 0);
    t.end();
  });
});
