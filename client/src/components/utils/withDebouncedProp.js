import React from 'react';

import _debounce from 'debounce';

export const withDebouncedProp = (WrappedComponent, source, target, {
  delay = 500,
  debounce = _debounce,
  debouncingProps = null
} = {}) => {
  class WithDebouncedProp extends React.Component {
    constructor(props) {
      super(props);
      this.state = {
        debouncing: false,
        data: source(props)
      };

      this.updateDataNow = () => {
        const data = source(this.props);
        this.setState({ debouncing: false, data });
      };

      this.updateDataDebounced = debounce(this.updateDataNow, delay);
    }

    componentDidUpdate(prevProps, prevState) {
      if (source(prevProps) != source(this.props)) {
        this.setState({ debouncing: true });
        this.updateDataDebounced();
      }
    }

    render() {
      let props = {
        ...this.props,
        ...target(this.state.data)
      };
      if (this.state.debouncing && debouncingProps) {
        props = {
          ...props,
          ...debouncingProps(props)
        }
      };
      return <WrappedComponent {...props} />;
    }
  }

  return WithDebouncedProp;
};

export default withDebouncedProp;
