import { withProps } from 'recompose';

import { createHashHistory } from "history";

export const withHashHistory = withProps(props => ({
  ...props,
  history: createHashHistory()
}));

export default withHashHistory;
