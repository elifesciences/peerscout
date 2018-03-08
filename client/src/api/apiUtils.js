export const getAuhenticationHeaders = authenticationState => ({
  headers: {
    'X-Access-Token': authenticationState && authenticationState.access_token
  }
});
