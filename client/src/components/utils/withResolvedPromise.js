import { compose, mapProps } from 'recompose';

import { withLoadingErrorIndicator } from '../state/withLoadingErrorIndicator';

const mapPromiseValueProp = propName => mapProps(
  props => ({
    ...props,
    [propName]: props[propName].value
  })
);

export const withResolvedPromise = (propName, options = {}) => compose(
  withLoadingErrorIndicator({
    ...options,
    isLoading: props => props[propName].loading,
    getError: props => props[propName].error
  }),
  mapPromiseValueProp(propName)
);

export default withResolvedPromise;
