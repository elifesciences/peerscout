import { WebAuth } from 'auth0-js';

import { Auth0LockPasswordless } from 'auth0-lock';

const ACCESS_TOKEN_KEY = 'access_token';

export const SESSION_EXPIRED_ERROR_MESSAGE = 'Session expired'

export const getAuthErrorMessage = error => {
  if (error && typeof(error) === 'string') {
    return error;
  }
  return SESSION_EXPIRED_ERROR_MESSAGE;
};

export default class Auth {
  constructor(options) {
    this.options = options;
    this.storage = options.storage || global.localStorage;
    this.WebAuth = options.WebAuth || WebAuth;
    this.Auth0LockPasswordless = options.Auth0LockPasswordless || Auth0LockPasswordless;
    this.lock = new this.Auth0LockPasswordless(
      options.client_id, options.domain, {
        passwordlessMethod: "link"
      }
    );
    this.initialising = true;
    this.lock.on('authorization_error', error => {
      console.log('authorization_error:', error);
      this._setAuthorizationError(error.errorDescription || error.error)
    });
    this.lock.on('authenticated', authResult => {
      console.log('authResult:', authResult)
      this._setAccessToken(authResult.accessToken);
    });
    this.lock.on('hash_parsed', hash => {
      console.log('hash_parsed, hash:', hash);
      if (!hash) {
        this._checkExistingToken();
      }
      this.initialising = false;
      if (!this.isAuthenticating()) {
        this._triggerStateChange();
      }
    });
    this.profile = null;
    this.listeners = [];
  }

  _checkExistingToken() {
    const access_token = this.storage.getItem(ACCESS_TOKEN_KEY);
    console.log('_checkExistingToken, access_token:', access_token);
    if (access_token) {
      this._setAccessToken(access_token);
    }
  }

  initialise() {
    // do nothing, it's now handled by Auth0 / after hash_parsed event
  }

  // The _doAuthentication function will get the user profile information if authentication is successful
  _setAccessToken(access_token, error_description) {
    console.log('_setAccessToken', !!access_token, error_description);
    if (access_token !== this.access_token) {
      this.access_token = access_token;
      this.error_description = error_description;
      if (access_token) {
        this.storage.setItem(ACCESS_TOKEN_KEY, access_token);
        this._userInfo(access_token, (err, user) => {
          if (err) {
            this._setAuthorizationError(getAuthErrorMessage(err));
          } else {
            console.log('logged user:', user);
            this.email = user.email;
            console.log('logged in email:', this.email);
            this._triggerStateChange();
          }
        });
      } else {
        this.storage.removeItem(ACCESS_TOKEN_KEY);
        this.email = null;
      }
      this._triggerStateChange();
    } else if (error_description !== this.error_description) {
      this.error_description = error_description;
      this._triggerStateChange();
    }
  }
 
  // We’ll display an error if the user clicks an outdated or invalid magiclink
  _setAuthorizationError(error_description) {
    console.error('There was an error:', error_description);
    this._setAccessToken(null, error_description);
  }

  _triggerStateChange() {
    this.listeners.forEach(listener => {
      listener(this.getAuthenticationState());
    })
  }

  getAuthenticationState() {
    return {
      authenticating: this.isAuthenticating(),
      authenticated: this.isAuthenticated(),
      logged_in: this.isAuthenticated(),
      access_token: this.access_token,
      email: this.email
    };
  }

  _userInfo(access_token, callback) {
    const auth0 = new this.WebAuth({
      domain: this.options.domain,
      clientID: this.options.client_id
    });
    return auth0.client.userInfo(access_token, callback);
  }

  revalidateToken() {
    const access_token = this.storage.getItem(ACCESS_TOKEN_KEY);
    if (access_token) {
      this.storage.setItem(ACCESS_TOKEN_KEY, access_token);
      this._userInfo(access_token, (err, user) => {
        if (err) {
          this._setAuthorizationError(SESSION_EXPIRED_ERROR_MESSAGE);
        } else {
          this.email = user.email;
        }
      });
    }
  }

  onStateChange(listener) {
    this.listeners.push(listener);
  }

  getAccessToken() {
    return this.access_token;
  }

  isAuthenticating() {
    return (!!this.access_token || this.initialising) && !this.isAuthenticated();
  }

  isAuthenticated() {
    return !!this.access_token && this.email;
  }

  loginUsingMagicLink() {
    this.lock.show();
  }

  logout() {
    const access_token = this.access_token;
    if (access_token) {
      this._setAccessToken(null);
      this.lock.logout({returnTo: window.location.href});
    }
  }
};
