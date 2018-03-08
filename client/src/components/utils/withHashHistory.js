import { withProps } from 'recompose';

import createHashHistory from 'history/createHashHistory';

export const withHashHistory = withProps(props => ({
  ...props,
  history: createHashHistory()
}));

export default withHashHistory;
