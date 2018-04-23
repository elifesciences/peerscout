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

const ERROR_MESSAGE_1 = 'error message 1';

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
const lastCall = mock => {
  const c = last(mock.getCalls());
  if (!c) {
    throw new Error(`expected call - ${mock}`);
  }
  return c;
};

const namedStub = name => {
  const stub = sinon.stub();
  stub.toString = () => `stub "${name}"`;
  return stub;
};

const createMockStorage = () => {
  const data = {};
  const storage = {
    _getItem: key => data[key],
    _setItem: (key, value) => { data[key] = value; },
    _removeItem: key => { delete data[key]; }
  };
  return {
    ...storage,
    getItem: sinon.spy(storage, '_getItem'),
    setItem: sinon.spy(storage, '_setItem'),
    removeItem: sinon.spy(storage, '_removeItem')
  };
};

const createMockLock = () => {
  const handlerMap = {};
  const on = (event, handler) => {
    handlerMap[event] = handler
  };
  const getUserInfo = namedStub('getUserInfo');
  const checkSession = namedStub('checkSession');
  const callbackUserInfo = (error, user) => lastCall(getUserInfo).args[1](error, user);
  const callbackCheckSession = (error, authResult) => lastCall(checkSession).args[1](error, authResult);
  return {
    on: sinon.spy(on),
    _trigger: (event, ...args) => handlerMap[event](...args),
    getUserInfo,
    checkSession,
    resolveUserInfo: user => callbackUserInfo(null, user),
    rejectUserInfo: error => callbackUserInfo(error, null),
    resolveCheckSession: authResult => callbackCheckSession(null, authResult),
    rejectCheckSession: error => callbackCheckSession(error, null)
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
    t.false(authTester.lock.checkSession.called, 'should call checkSession');

    t.false(authTester.lastState.authenticating, 'should not be authenticating');
    t.end();
  }));

  g.test('.should handle authorization error', withSandbox(t => {
    const authTester = createAuthTester(t);
    authTester.lock._trigger('hash_parsed', AUTH_HASH);

    authTester.lock._trigger('authorization_error', AUTHORIZATION_ERROR);
    t.true(authTester.onStateChangeHandler.called, 'should call onStateChangeHandler');

    const lastState = authTester.lastState || {};
    t.equal(lastState.error_description, AUTHORIZATION_ERROR.errorDescription);
    t.false(lastState.authenticating, 'should not be authenticating');
    t.false(lastState.authenticated, 'should not be authenticated');
    t.false(authTester.auth._wasLoggedIn(), 'should not be marked as logged in');
    t.end();
  }));

  g.test('.should handle authenticated with valid user profile', withSandbox(t => {
    const authTester = createAuthTester(t);
    authTester.lock._trigger('hash_parsed', AUTH_HASH);
    authTester.lock._trigger('authenticated', AUTH_RESULT);
    t.true(authTester.auth.isAuthenticating(), 'should be authenticating still');
    t.false(authTester.auth.isAuthenticated(), 'should not be authenticated yet');

    authTester.lock.resolveUserInfo(USER);
    t.true(authTester.onStateChangeHandler.called, 'should call onStateChangeHandler');

    const lastState = authTester.lastState || {};
    t.equal(lastState.email, EMAIL);
    t.equal(lastState.error_description, null);
    t.equal(lastState.access_token, AUTH_RESULT.accessToken);
    t.false(lastState.authenticating, 'should not be authenticating');
    t.true(lastState.authenticated, 'should be authenticated');
    t.true(authTester.auth._wasLoggedIn(), 'should be marked as logged in');
    t.end();
  }));

  g.test('.should handle authenticated with invalid user profile', withSandbox(t => {
    const authTester = createAuthTester(t);
    authTester.auth._saveLoggedIn(true);
    authTester.lock._trigger('hash_parsed', AUTH_HASH);
    authTester.lock._trigger('authenticated', AUTH_RESULT);
    t.true(authTester.auth.isAuthenticating(), 'should be authenticating still');
    t.false(authTester.auth.isAuthenticated(), 'should not be authenticated yet');

    authTester.lock.rejectUserInfo(USER_INFO_ERROR_OBJ);
    t.true(authTester.onStateChangeHandler.called, 'should call onStateChangeHandler');

    const lastState = authTester.lastState;
    t.equal(lastState.error_description, getAuthErrorMessage(USER_INFO_ERROR_OBJ));
    t.equal(lastState.access_token, null);
    t.false(lastState.authenticating, 'should not be authenticating');
    t.false(lastState.authenticated, 'should be authenticated');
    t.end();
  }));

  g.test('.should handle authenticated from saved access token and valid user profile', withSandbox(t => {
    const authTester = createAuthTester(t);
    authTester.auth._saveLoggedIn(true);
    authTester.lock._trigger('hash_parsed', null);

    authTester.lock.resolveCheckSession(AUTH_RESULT);

    t.true(authTester.auth.isAuthenticating(), 'should be authenticating still');
    t.false(authTester.auth.isAuthenticated(), 'should not be authenticated yet');

    authTester.lock.resolveUserInfo(USER);
    t.true(authTester.onStateChangeHandler.called, 'should call onStateChangeHandler');

    const lastState = authTester.lastState || {};
    t.equal(lastState.email, EMAIL);
    t.equal(lastState.error_description, null);
    t.equal(lastState.access_token, AUTH_RESULT.accessToken);
    t.false(lastState.authenticating, 'should not be authenticating');
    t.true(lastState.authenticated, 'should be authenticated');
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

  g.test('.should return error_description if it is a string', t => {
    t.equal(getAuthErrorMessage({error_description: ERROR_MESSAGE_1}), ERROR_MESSAGE_1);
    t.end();
  });

  g.test('.should return session expired error if error.error_description is an object', t => {
    t.equal(getAuthErrorMessage({error_description: USER_INFO_ERROR_OBJ}), SESSION_EXPIRED_ERROR_MESSAGE);
    t.end();
  });
});
