import React from 'react';
import { createSelector } from 'reselect';
import debounce from 'debounce';
import createHashHistory from 'history/createHashHistory';
import equals from 'deep-equal';

import {
  LoadingIndicator,
  View
} from '../../components';

import SearchHeader from './SearchHeader';
import SearchResult from './SearchResult';

const styles = {
  containerWithMargin: {
    margin: 8
  }
}

const parseSearch = search => {
  const q = search[0] === '?' ? search.substring(1) : search;
  const params = {};
  q.split('&').forEach(s => {
    const index = s.indexOf('=');
    const name = index >= 0 ? s.substring(0, index) : s;
    const value = index >= 0 ? decodeURIComponent(s.substring(index + 1)) : undefined;
    params[name] = value;
  });
  return params;
}

class Main extends React.Component {
  constructor(props) {
    super(props);
    this.history = createHashHistory({});
    this.defaultSearchOptions = {
      manuscriptNumber: '',
      keywords: ''
    };
    this.state = {
      searchOptions: this.defaultSearchOptions,
      reqId: 0
    };

    this.getResults = createSelector(
      () => this.state.searchOptions,
      (searchOptions) => {
        if (!searchOptions.keywords && !searchOptions.manuscriptNumber) {
          return Promise.resolve();
        }
        return this.props.reviewerRecommendationApi.recommendReviewers({
          keywords: searchOptions.keywords,
          manuscript_no: searchOptions.manuscriptNumber
        });
      }
    );

    this.doUpdateResultsNow = () => {
      this.actuallyLoading = true;
      const resultsSearchOptions = this.state.searchOptions;
      this.getResults().then(resultsResponse => {
        console.log("resultsResponse:", resultsResponse);
        this.actuallyLoading = false;
        this.setState({
          results: resultsResponse && {
            potentialReviewers: resultsResponse['potential-reviewers'],
            matchingManuscripts: resultsResponse['matching-manuscripts'],
            manuscriptsNotFound: resultsResponse['manuscripts-not-found']
          },
          resultsSearchOptions,
          shouldLoad: false,
          loading: false
        });
      });
    };

    this.updateResultsNow = () => {
      this.setState(state => ({
        ...state,
        loading: true,
        shouldLoad: true
      }));
    };

    this.updateResultsDebounced = debounce(this.updateResultsNow, 500);

    this.updateResults = () => {
      this.setState({
        loading: true
      });
      this.updateResultsDebounced();
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
    const path = '/search?' +
      Object.keys(searchOptions)
      .filter(k => !!searchOptions[k])
      .map(k => `${k}=${encodeURIComponent(searchOptions[k])}`)
      .join('&');
    if (path !== (this.history.location.pathname + this.history.location.search)) {
      this.history.push(path);
    }
  }

  setSearchOptions(searchOptions) {
    if (!equals(this.state.searchOptions, searchOptions)) {
      this.setState({
        searchOptions
      });
      this.updateResults();
    }
  }

  updateSearchOptionsFromLocation(location) {
    this.setSearchOptions(this.locationToSearchOptions(
      location, this.defaultSearchOptions
    ));
  }

  componentDidMount() {
    this.updateSearchOptionsFromLocation(this.history.location);
    this.unlisten = this.history.listen((location, action) => {
      this.updateSearchOptionsFromLocation(location);
    });
  }

  componentDidUpdate(prevProps, prevState) {
    if (
      (this.state.shouldLoad) &&
      (!this.actuallyLoading)
    ) {
      this.pushSearchOptions(this.state.searchOptions);
      this.doUpdateResultsNow();
    }
  }

  updateOption(state) {
    this.setState(state);
  }

  onSearchOptionsChanged = searchOptions => {
    this.setSearchOptions(searchOptions);
  }

  render() {
    const {
      loading,
      searchOptions,
      results
    } = this.state;
    return (
      <View>
        <SearchHeader
          searchOptions={ searchOptions }
          onSearchOptionsChanged={ this.onSearchOptionsChanged }
        />
        <View style={ styles.containerWithMargin }>
          <LoadingIndicator loading={ loading }>
            <View>
              {
                results && (
                  <SearchResult searchResult={ results }/>
                )
              }
            </View>
          </LoadingIndicator>
        </View>
      </View>
    );
  }
}

export default Main;
