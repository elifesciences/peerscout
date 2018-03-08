import { withProps } from 'recompose';

export const withLocalStorage = withProps({
  localStorage: global.localStorage
});

export default withLocalStorage;
