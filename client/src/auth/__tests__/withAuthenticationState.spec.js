import React from 'react';

import test from 'tape';
import { shallow, mount } from 'enzyme';
import sinon from 'sinon';

import withSandbox from '../../utils/__tests__/withSandbox';

import withAuthenticationState from '../withAuthenticationState';

import * as AuthModule from '../Auth';
import * as NullAuthModule from '../NullAuth';

import deferred from 'deferred';

const WrappedComponent = props => (<div></div>);

const NO_AUTH_CONFIG = {};
const AUTH0_CONFIG = {
  auth0_domain: 'auth0_domain1',
  auth0_client_id: 'auth0_client_id1'
};

const NOT_AUTHENTICATED = {
  authenticated: false
};

const AUTHENTICATED = {
  authenticated: true
};

const createMockAuth = () => ({
  onStateChange: sinon.stub(),
  getAuthenticationState: sinon.stub(),
  initialise: sinon.stub()
});

test('withAuthenticationState', g => {
  g.test('.should be defined', t => {
    t.true(withAuthenticationState);
    t.end();
  });

  g.test('.should pass custom prop to wrapped component', t => {
    const Component = withAuthenticationState(WrappedComponent);
    const component = shallow(<Component other="123" config={ NO_AUTH_CONFIG } />);
    const wrappedComponent = component.find('WrappedComponent');
    t.equal(wrappedComponent.props()['other'], '123');
    t.end();
  });

  g.test('.should use NullAuth and pass to wrapped component', withSandbox(t => {
    const auth = createMockAuth();
    const NullAuth = t.sandbox.stub(NullAuthModule, 'default').returns(auth);

    const Component = withAuthenticationState(WrappedComponent);
    const component = shallow(<Component config={ NO_AUTH_CONFIG } />);
    t.true(NullAuth.calledOnce);
    const wrappedComponent = component.find('WrappedComponent');
    t.equal(wrappedComponent.props()['auth'], auth);
    t.end();
  }));

  g.test('.should use Auth and pass to wrapped component', withSandbox(t => {
    const auth = createMockAuth();
    const NullAuth = t.sandbox.stub(AuthModule, 'default').returns(auth);

    const Component = withAuthenticationState(WrappedComponent);
    const component = shallow(<Component config={ AUTH0_CONFIG } />);
    t.true(NullAuth.calledWith({
      domain: AUTH0_CONFIG.auth0_domain,
      client_id: AUTH0_CONFIG.auth0_client_id
    }));
    t.true(NullAuth.calledOnce);
    const wrappedComponent = component.find('WrappedComponent');
    t.equal(wrappedComponent.props()['auth'], auth);
    t.end();
  }));

  g.test('.should pass initial authenticationState to wrapped component', withSandbox(t => {
    const auth = createMockAuth();
    const NullAuth = t.sandbox.stub(AuthModule, 'default').returns(auth);
    auth.getAuthenticationState.returns(NOT_AUTHENTICATED);

    const Component = withAuthenticationState(WrappedComponent);
    const component = shallow(<Component config={ AUTH0_CONFIG } />);
    const wrappedComponent = component.find('WrappedComponent');
    t.equal(wrappedComponent.props()['authenticationState'], NOT_AUTHENTICATED);
    t.end();
  }));

  g.test('.should update authenticationState of wrapped component', withSandbox(t => {
    const auth = createMockAuth();
    const NullAuth = t.sandbox.stub(AuthModule, 'default').returns(auth);
    auth.getAuthenticationState.returns(NOT_AUTHENTICATED);

    const Component = withAuthenticationState(WrappedComponent);
    const component = shallow(<Component config={ AUTH0_CONFIG } />);
    const onStateChangeHandler = auth.onStateChange.getCall(0).args[0];
    onStateChangeHandler(AUTHENTICATED);
    component.setState({});
    const wrappedComponent = component.find('WrappedComponent');
    t.equal(wrappedComponent.props()['authenticationState'], AUTHENTICATED);
    t.end();
  }));
});
