import React from 'react';

import Auth from './Auth';
import NullAuth from './NullAuth';

const createAuthForConfig = config => {
  if (config.auth0_domain && config.auth0_client_id) {
    return new Auth({
      domain: config.auth0_domain,
      client_id: config.auth0_client_id
    });
  } else {
    return new NullAuth();
  }
};

const withAuthenticationState = WrappedComponent => {
  class WithAuthenticationState extends React.Component {
    constructor(props) {
      super(props);

      const { config } = props;
      this.auth = createAuthForConfig(config);
  
      this.auth.onStateChange(authenticationState => {
        this.setState({
          authenticationState
        });
      });

      this.state = {
        authenticationState: this.auth.getAuthenticationState()
      };
    }

    componentDidMount() {
      this.auth.initialise();
    }

    render() {
      const { authenticationState } = this.state;
      return <WrappedComponent
        { ...this.props }
        authenticationState={ authenticationState }
        auth={ this.auth }
      />
    }
  }

  return WithAuthenticationState;
};

export default withAuthenticationState;
