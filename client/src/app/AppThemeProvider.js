import React from 'react';
import MuiThemeProvider from 'material-ui/styles/MuiThemeProvider';

const AppThemeProvider = props => (
  <MuiThemeProvider>
    { props.children }
  </MuiThemeProvider>
);

export default AppThemeProvider;
