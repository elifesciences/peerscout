import withAuthenticationState from './withAuthenticationState';
import withLoginForm from './withLoginForm';

const withAuthenticatedAuthenticationState = WrappedComponent => withAuthenticationState(
  withLoginForm(WrappedComponent)
);

export default withAuthenticatedAuthenticationState;
