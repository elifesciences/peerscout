import React from 'react';

const LOADING_RESULT = {
  loading: true
};

export const withPromisedProp = (WrappedComponent, load, propName, updateOn) => {
  class WithPromisedProp extends React.Component {
    constructor(props) {
      super(props);
      this.state = { result: LOADING_RESULT };
      this._mounted = false;
    }

    _setResult(result) {
      if (this._mounted) {
        super.setState({result});
      } else {
        // save the result, in case we're coming back
        this.state = { ...this.state, result };
      }
    }

    triggerLoad() {
      this._setResult(LOADING_RESULT);
      load(this.props).then(value => this._setResult({
        loading: false,
        value
      })).catch(error => this._setResult({
        loading: false,
        error
      }));
    }

    componentDidMount() {
      this._mounted = true;
      this.triggerLoad();
    }

    componentWillUnmount() {
      this._mounted = false;
    }

    componentDidUpdate(prevProps, prevState) {
      if (updateOn && (updateOn(prevProps) != updateOn(this.props))) {
        this.triggerLoad();
      }
    }

    render() {
      const props = {
        ...this.props,
        [propName]: this.state.result
      };
      return <WrappedComponent {...props} />;
    }
  }

  return WithPromisedProp;
};

export default withPromisedProp;
