import React from 'react';

const withPromisedProp = (WrappedComponent, load, propName, updateOn) => {
  class WithPromisedProp extends React.Component {
    constructor(props) {
      super(props);
      this.state = {
        result: {
          loading: true
        }
      };
    }

    triggerLoad() {
      load(this.props).then(value => this.setState({
        result: {
          loading: false,
          value
        }
      })).catch(error => this.setState({
        result: {
          loading: false,
          error
        }
      }));
    }

    componentDidMount() {
      this.triggerLoad();
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
