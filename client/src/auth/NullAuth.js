export default class NullAuth {
  constructor(options) {
  }

  initialise() {
  }

  getAuthenticationState() {
    return {
      authenticating: false,
      authenticated: true,
      logged_in: false,
      access_token: null,
      email: null
    };
  }

  onStateChange(listener) {
  }

  getAccessToken() {
    return this.access_token;
  }

  isLoggedIn() {
    return false;
  }

  isAuthenticating() {
    return false;
  }

  isAuthenticated() {
    return true;
  }

  logout() {
  }
};
