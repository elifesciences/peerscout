import {
  WebAuth
} from 'auth0-js';
import Auth0LockPasswordless from 'auth0-lock-passwordless';

const ACCESS_TOKEN_KEY = 'access_token';

export default class Auth {
  constructor(options) {
    this.options = options;
    this.lock = new Auth0LockPasswordless(
      options.client_id, options.domain
    );
    this.profile = null;
    this.listeners = [];
  }

  initialise() {
    console.log('initialise', window.location.hash);
    const hash_auth_result = this.lock.parseHash(window.location.hash);
    console.log('hash_auth_result', hash_auth_result);
    if (hash_auth_result && hash_auth_result.error) {
      this._setAuthorizationError(hash_auth_result.error_description || hash_auth_result.error)
    } else if (hash_auth_result && hash_auth_result.access_token) {
      this._setAccessToken(hash_auth_result.access_token);
    } else {
      const access_token = localStorage.getItem(ACCESS_TOKEN_KEY);
      if (access_token) {
        this._setAccessToken(access_token);
      }
    }
  }

  // The _doAuthentication function will get the user profile information if authentication is successful
  _setAccessToken(access_token) {
    console.log('_setAccessToken', !!access_token);
    if (access_token !== this.access_token) {
      this.access_token = access_token;
      if (access_token) {
        localStorage.setItem(ACCESS_TOKEN_KEY, access_token);
        this._userInfo(access_token, (err, user) => {
          if (err) {
            this._setAuthorizationError(err);
          } else {
            console.log('logged user:', user);
            this.email = user.email;
            console.log('logged in email:', this.email);
            this._triggerStateChange();
          }
        });
      } else {
        localStorage.removeItem(ACCESS_TOKEN_KEY);
        this.email = null;
      }
      this._triggerStateChange();
    }
  }
 
  // We’ll display an error if the user clicks an outdated or invalid magiclink
  _setAuthorizationError(error_description) {
    this._setAccessToken(null);
    this.error_description = error_description;
    console.error('There was an error: ' + error_description);
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
    const auth0 = new WebAuth({
      domain: this.options.domain,
      clientID: this.options.client_id
    });
    return auth0.client.userInfo(access_token, callback);
  }

  revalidateToken() {
    const access_token = localStorage.getItem(ACCESS_TOKEN_KEY);
    if (access_token) {
      localStorage.setItem(ACCESS_TOKEN_KEY, access_token);
      this._userInfo(access_token, (err, user) => {
        if (err) {
          this._setAuthorizationError(err);
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
    return !!this.access_token && !this.email;
  }

  isAuthenticated() {
    return !!this.access_token && this.email;
  }

  loginUsingMagicLink() {
    this.lock.magiclink();
  }

  logout() {
    const access_token = this.access_token;
    if (access_token) {
      this._setAccessToken(null);
      this.lock.logout({returnTo: window.location.href});
    }
  }
};
