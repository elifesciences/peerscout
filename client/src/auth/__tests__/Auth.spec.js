import React from 'react';

import test from 'tape';
import { shallow, mount } from 'enzyme';
import sinon from 'sinon';

import withSandbox from '../../utils/__tests__/withSandbox';

import Auth, { getAuthErrorMessage, SESSION_EXPIRED_ERROR_MESSAGE } from '../Auth';

import * as Auth0LockModule from 'auth0-lock';

import deferred from 'deferred';

const EMAIL = 'john@doh.org';
const USER = {email: EMAIL};
const AUTH_HASH = 'authHash1';

const NO_AUTH_CONFIG = {};
const AUTH0_CONFIG = {
  domain: 'auth0_domain1',
  client_id: 'auth0_client_id1'
};

const AUTHORIZATION_ERROR = {
  errorDescription: 'not authorized',
  error: 1234
};

const USER_INFO_ERROR = 'invalid user';

const USER_INFO_ERROR_OBJ = {
  code: 401,
  statusCode: 401,
  name: 'Error'
};

const AUTH_RESULT = {
  accessToken: 'access1'
};

const NOT_AUTHENTICATED = {
  authenticated: false
};

const AUTHENTICATED = {
  authenticated: true
};

const last = list => list[list.length - 1];
const lastCall = mock => last(mock.getCalls());

const createMockStorage = () => ({
  getItem: sinon.stub(),
  setItem: sinon.stub(),
  removeItem: sinon.stub()
});

const createMockLock = () => {
  const handlerMap = {};
  const on = (event, handler) => {
    handlerMap[event] = handler
  };
  const getUserInfo = sinon.stub();
  const callbackUserInfo = (error, user) => lastCall(getUserInfo).args[1](error, user);
  return {
    on: sinon.spy(on),
    _trigger: (event, ...args) => handlerMap[event](...args),
    getUserInfo,
    resolveUserInfo: user => callbackUserInfo(null, user),
    rejectUserInfo: error => callbackUserInfo(error, null)
  };
};

const createAuthTester = (t, config = AUTH0_CONFIG) => {
  const lock = createMockLock();
  const Auth0LockPasswordless = t.sandbox.stub(Auth0LockModule, 'Auth0LockPasswordless');
  Auth0LockPasswordless.returns(lock);

  const storage = createMockStorage();

  const auth = new Auth({
    ...config,
    storage,
    Auth0LockPasswordless
  });

  const authTester = {
    lock,
    Auth0LockPasswordless,
    storage,
    auth
  };

  const onStateChangeHandler = state => {
    authTester.lastState = state;
  };

  authTester.onStateChangeHandler = sinon.spy(onStateChangeHandler);
  auth.onStateChange(authTester.onStateChangeHandler);

  return authTester;
};

test('Auth', g => {
  g.test('.should be defined', t => {
    t.true(Auth);
    t.end();
  });

  g.test('.should pass configuration to Auth0LockPasswordless', withSandbox(t => {
    const authTester = createAuthTester(t);
    t.true(authTester.Auth0LockPasswordless.calledWith(
      AUTH0_CONFIG.client_id,
      AUTH0_CONFIG.domain, {
        passwordlessMethod: "link"
      }
    ), 'called with configuration, was: ' + authTester.Auth0LockPasswordless.getCalls());
    t.end();
  }));

  g.test('.should be indicate authenticating before hash is loaded', withSandbox(t => {
    const authTester = createAuthTester(t);
    t.true(authTester.auth.isAuthenticating(), 'should be authenticating');
    t.end();
  }));

  g.test('.should not be indicate authenticating after empty hash is loaded with no saved access token', withSandbox(t => {
    const authTester = createAuthTester(t);
    t.true(authTester.auth.isAuthenticating(), 'should be authenticating still');
    authTester.lock._trigger('hash_parsed', null);
    t.true(authTester.onStateChangeHandler.called, 'should call onStateChangeHandler');
    t.false(authTester.lastState.authenticating, 'should not be authenticating');
    t.end();
  }));

  g.test('.should handle authorization error', withSandbox(t => {
    const authTester = createAuthTester(t);
    authTester.lock._trigger('hash_parsed', AUTH_HASH);
    authTester.lock._trigger('authorization_error', AUTHORIZATION_ERROR);
    t.equal(authTester.auth.error_description, AUTHORIZATION_ERROR.errorDescription);
    t.true(authTester.onStateChangeHandler.called, 'should call onStateChangeHandler');
    t.false(authTester.lastState.authenticating, 'should not be authenticating');
    t.false(authTester.lastState.authenticated, 'should not be authenticated');
    t.end();
  }));

  g.test('.should handle authenticated with valid user profile', withSandbox(t => {
    const authTester = createAuthTester(t);
    authTester.lock._trigger('hash_parsed', AUTH_HASH);
    authTester.lock._trigger('authenticated', AUTH_RESULT);
    t.true(authTester.auth.isAuthenticating(), 'should be authenticating still');
    t.false(authTester.auth.isAuthenticated(), 'should not be authenticated yet');

    authTester.lock.resolveUserInfo(USER);
    t.equal(authTester.auth.email, EMAIL);
    t.equal(authTester.auth.error_description, undefined);
    t.equal(authTester.auth.access_token, AUTH_RESULT.accessToken);
    t.true(authTester.onStateChangeHandler.called, 'should call onStateChangeHandler');
    t.false(authTester.lastState.authenticating, 'should not be authenticating');
    t.true(authTester.lastState.authenticated, 'should be authenticated');
    t.end();
  }));

  g.test('.should handle authenticated with invalid user profile', withSandbox(t => {
    const authTester = createAuthTester(t);
    authTester.lock._trigger('hash_parsed', AUTH_HASH);
    authTester.lock._trigger('authenticated', AUTH_RESULT);
    t.true(authTester.auth.isAuthenticating(), 'should be authenticating still');
    t.false(authTester.auth.isAuthenticated(), 'should not be authenticated yet');

    authTester.lock.rejectUserInfo(USER_INFO_ERROR_OBJ);
    t.equal(authTester.auth.error_description, getAuthErrorMessage(USER_INFO_ERROR_OBJ));
    t.equal(authTester.auth.access_token, null);
    t.true(authTester.onStateChangeHandler.called, 'should call onStateChangeHandler');
    t.false(authTester.lastState.authenticating, 'should not be authenticating');
    t.false(authTester.lastState.authenticated, 'should be authenticated');
    t.end();
  }));

  g.test('.should handle authenticated from saved access token and valid user profile', withSandbox(t => {
    const authTester = createAuthTester(t);
    authTester.storage.getItem.returns(AUTH_RESULT.accessToken);
    authTester.lock._trigger('hash_parsed', null);
    t.true(authTester.auth.isAuthenticating(), 'should be authenticating still');
    t.false(authTester.auth.isAuthenticated(), 'should not be authenticated yet');

    authTester.lock.resolveUserInfo(USER);
    t.equal(authTester.auth.email, EMAIL);
    t.equal(authTester.auth.error_description, undefined);
    t.equal(authTester.auth.access_token, AUTH_RESULT.accessToken);
    t.true(authTester.onStateChangeHandler.called, 'should call onStateChangeHandler');
    t.false(authTester.lastState.authenticating, 'should not be authenticating');
    t.true(authTester.lastState.authenticated, 'should be authenticated');
    t.end();
  }));
});

test('Auth.getAuthErrorMessage', g => {
  g.test('.should return error if error is a non-empty string', t => {
    t.equal(getAuthErrorMessage(USER_INFO_ERROR), USER_INFO_ERROR);
    t.end();
  });

  g.test('.should return session expired error if error is an empty string', t => {
    t.equal(getAuthErrorMessage(''), SESSION_EXPIRED_ERROR_MESSAGE);
    t.end();
  });

  g.test('.should return session expired error if error is an object', t => {
    t.equal(getAuthErrorMessage(USER_INFO_ERROR_OBJ), SESSION_EXPIRED_ERROR_MESSAGE);
    t.end();
  });
});
