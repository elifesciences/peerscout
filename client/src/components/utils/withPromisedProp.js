import React from 'react';

import { lifecycle, defaultProps, compose } from 'recompose';

const LOADING_RESULT = {
  loading: true
};

export const withPromisedPropEnhancer = (load, propName, updateOn) => compose(
  defaultProps({
    [propName]: LOADING_RESULT
  }),

  lifecycle({
    _setResult(result) {
      this.setState({
        [propName]: result
      });
    },

    triggerLoad() {
      this._setResult(LOADING_RESULT);
      load(this.props).then(value => this._setResult({
        loading: false,
        value
      })).catch(error => this._setResult({
        loading: false,
        error
      }));
    },

    componentDidMount() {
      this.triggerLoad();
    },

    componentDidUpdate(prevProps, prevState) {
      if (updateOn && (updateOn(prevProps) != updateOn(this.props))) {
        this.triggerLoad();
      }
    }
  })
);

export const withPromisedProp = (WrappedComponent, load, propName, updateOn) => (
  withPromisedPropEnhancer(load, propName, updateOn)(WrappedComponent)
);

export default withPromisedProp;
