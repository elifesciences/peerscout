import React from 'react';

import equals from 'deep-equal';

export const parseSearch = search => {
  const q = search[0] === '?' ? search.substring(1) : search;
  const params = {};
  q.split('&').forEach(s => {
    const index = s.indexOf('=');
    const name = index >= 0 ? s.substring(0, index) : s;
    const value = index >= 0 ? decodeURIComponent(s.substring(index + 1)) : undefined;
    params[name] = value;
  });
  return params;
};

export const withSearchOptions = WrappedComponent => {
  class WithSearchOptions extends React.Component {
    constructor(props) {
      super(props);
      const { config, searchTypes } = props;

      this.unlisten = props.history.listen((location, action) => {
        this.updateSearchOptionsFromLocation(location);
      });
  
      this.defaultSearchOptions = {
        manuscriptNumber: '',
        keywords: ''
      };

      if (searchTypes && searchTypes.length > 0) {
        this.defaultSearchOptions.searchType = searchTypes[0].search_type;
      }

      this.state = {
        searchOptions: this.defaultSearchOptions
      };

      this.staticProps = {
        setSearchOptions: this.setSearchOptions.bind(this),
        pushSearchOptions: this.pushSearchOptions.bind(this)
      };
    }

    locationToSearchOptions(location, defaultSearchOptions) {
      const params = parseSearch(location.search || '');
      return {
        ...defaultSearchOptions,
        ...params
      };
    }
  
    pushSearchOptions(searchOptions) {
      const path = ['/search',
        Object.keys(searchOptions)
        .filter(k => !!searchOptions[k])
        .filter(k => typeof searchOptions[k] === 'string')
        .map(k => `${k}=${encodeURIComponent(searchOptions[k])}`)
        .join('&')].filter(s => !!s).join('?');
      if (path !== (this.props.history.location.pathname + this.props.history.location.search)) {
        this.props.history.push(path);
      }
    }
  
    setSearchOptions(searchOptions) {
      if (!equals(this.state.searchOptions, searchOptions)) {
        this.setState({
          searchOptions
        });
      }
    }
  
    updateSearchOptionsFromLocation(location) {
      this.setSearchOptions(this.locationToSearchOptions(
        location, this.defaultSearchOptions
      ));
    }
  
    componentDidMount() {
      this.updateSearchOptionsFromLocation(this.props.history.location);
    }

    render() {
      const props = {
        ...this.props,
        ...this.staticProps,
        searchOptions: this.state.searchOptions
      }
      return <WrappedComponent { ...props } />
    }
  }

  return WithSearchOptions;
};
