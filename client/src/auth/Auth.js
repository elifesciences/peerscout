import { Auth0LockPasswordless } from 'auth0-lock';

import equals from 'deep-equal';

const LOGGED_IN_KEY = 'logged_in';

export const SESSION_EXPIRED_ERROR_MESSAGE = 'Session expired'

export const getAuthErrorMessage = error => {
  if (error && typeof(error) === 'string') {
    return error;
  }
  if (error && error.error_description && typeof(error.error_description) === 'string') {
    return error.error_description;
  }
  return SESSION_EXPIRED_ERROR_MESSAGE;
};

const getAuthenticationState = ({
  access_token,
  email,
  initialising,
  error_description
}) => {
  const authenticated = !!access_token && email;
  const authenticating = (!!access_token || initialising) && !authenticated;
  return {
    authenticating,
    authenticated,
    error_description,
    logged_in: authenticated,
    access_token,
    email
  };
};

const EMPTY_STATE = {
  initialising: false,
  access_token: null,
  email: null,
  error_description: null
};

export default class Auth {
  constructor(options) {
    this.options = options;
    this.storage = options.storage || global.localStorage;
    this.Auth0LockPasswordless = options.Auth0LockPasswordless || Auth0LockPasswordless;
    this.lock = new this.Auth0LockPasswordless(
      options.client_id, options.domain, {
        passwordlessMethod: "link"
      }
    );

    this._state = {
      ...EMPTY_STATE,
      initialising: true
    };
    this._authenticationState = getAuthenticationState(this._state);

    this.lock.on('authorization_error', error => {
      console.log('authorization_error:', error);
      this._setAuthorizationError(error.errorDescription || error.error)
    });
    this.lock.on('authenticated', authResult => {
      console.log('authResult:', authResult)
      this._updateUserInfo(authResult.accessToken);
    });
    this.lock.on('hash_parsed', hash => {
      console.log('hash_parsed, hash:', hash);
      if (!hash) {
        this._checkExistingToken();
      }
    });
    this.profile = null;
    this.listeners = [];
  }

  // Was the user marked as logged in? (and should we check the access token etc.)
  _wasLoggedIn() {
    return !!this.storage.getItem(LOGGED_IN_KEY);
  }

  // saves the state whether a user is logged in (this should not be used as the authentication state)
  _saveLoggedIn(loggedIn) {
    if (loggedIn) {
      this.storage.setItem(LOGGED_IN_KEY, '1');
    } else {
      this.storage.removeItem(LOGGED_IN_KEY);
    }
  }

  _checkExistingToken() {
    if (this._wasLoggedIn()) {
      this._checkSession();
    } else {
      this._setState({
        initialising: false
      });
    }
  }

  initialise() {
    // do nothing, it's now handled by Auth0 / after hash_parsed event
  }

  _checkSession() {
    this._setState({
      initialising: true
    });
    this.lock.checkSession({}, (error, authResult) => {
      console.log('_checkSession', error, authResult);
      if (error || !authResult) {
        this._setAuthorizationError(getAuthErrorMessage(error));
      } else {
        this._updateUserInfo(authResult.accessToken);
      }
    });
  }

  _updateUserInfo(access_token) {
    this._setState({
      initialising: true
    });
    this._userInfo(access_token, (err, user) => {
      console.log('_updateUserInfo:', err, user);
      if (err) {
        this._setAuthorizationError(getAuthErrorMessage(err));
      } else {
        console.log('logged user:', user);
        const email = user.email;
        console.log('logged in email:', email);
        this._setState({
          access_token,
          initialising: false,
          email
        });
        this._saveLoggedIn(true);
      }
    });
  }
 
  // We’ll display an error if the user clicks an outdated or invalid magiclink
  _setAuthorizationError(error_description) {
    console.error('There was an error:', error_description);
    this._saveLoggedIn(false);
    this._setState({
      ...EMPTY_STATE,
      initialising: false,
      error_description
    });
  }

  _triggerStateChange() {
    this.listeners.forEach(listener => {
      listener(this.getAuthenticationState());
    });
  }

  _setState(state) {
    this._state = {
      ...this._state,
      ...state
    };
    console.log('this._state:', this._state);
    this._setAuthenticationState(getAuthenticationState(this._state));
  }

  _setAuthenticationState(authenticationState) {
    if (!equals(authenticationState, this._authenticationState)) {
      this._authenticationState = authenticationState;
      this._triggerStateChange();
    }
  }

  getAuthenticationState() {
    return this._authenticationState;
  }

  _userInfo(access_token, callback) {
    return this.lock.getUserInfo(access_token, callback);
  }

  revalidateToken() {
    this._checkSession();
  }

  onStateChange(listener) {
    this.listeners.push(listener);
  }

  getAccessToken() {
    return this.getAuthenticationState().access_token;
  }

  isAuthenticating() {
    return this.getAuthenticationState().authenticating;
  }

  isAuthenticated() {
    return this.getAuthenticationState().authenticated;
  }

  loginUsingMagicLink() {
    this.lock.show();
  }

  logout() {
    const access_token = this.getAccessToken();
    if (access_token) {
      this._saveLoggedIn(false);
      this._setState({
        initialising: false,
        access_token: null,
        email: null
      });
      this.lock.logout({returnTo: window.location.href});
    }
  }
};
