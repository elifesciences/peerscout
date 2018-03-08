import React from 'react';

import debounce from 'debounce';

export const withDebouncedProp = (WrappedComponent, source, target, delay = 500) => {
  class WithDebouncedProp extends React.Component {
    constructor(props) {
      super(props);
      this.state = {
        data: source(props)
      };

      this.updateDataNow = () => {
        const data = source(this.props);
        console.log('debounce, updating:', data);
        this.setState({ data });
      };

      this.updateDataDebounced = debounce(this.updateDataNow, delay);
    }

    componentDidUpdate(prevProps, prevState) {
      if (source(prevProps) != source(this.props)) {
        this.updateDataDebounced();
      }
    }


    render() {
      const props = {
        ...this.props,
        ...target(this.state.data)
      };
      console.log('debounce, render:', props);
      return <WrappedComponent {...props} />;
    }
  }

  return WithDebouncedProp;
};

export default withDebouncedProp;
