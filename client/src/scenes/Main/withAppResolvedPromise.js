import { mapProps } from 'recompose';

import withAppLoadingIndicator from './withAppLoadingIndicator';

const mapPromiseValueProp = propName => mapProps(
  props => ({
    ...props,
    [propName]: props[propName].value
  })
);

const withResolvedPromise = (WrappedComponent, propName) => withAppLoadingIndicator(
  mapPromiseValueProp(propName)(WrappedComponent),
  props => props[propName].loading,
  props => props[propName].error
);

export default withResolvedPromise;
