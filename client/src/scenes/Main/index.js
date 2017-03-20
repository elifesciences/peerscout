import React from 'react';
import { createSelector } from 'reselect';
import debounce from 'debounce';
import createHashHistory from 'history/createHashHistory';
import equals from 'deep-equal';
import SplitPane from 'react-split-pane';

import {
  LoadingIndicator,
  View
} from '../../components';

import SearchHeader from './SearchHeader';
import SearchResult from './SearchResult';
import ChartResult from './ChartResult';

const styles = {
  containerWithMargin: {
    flex: 1
  },
  resultsContainer: {
    position: 'relative',
    flex: 1,
    display: 'flex'
  },
  sceneContainer: {
    flex: 1
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
          manuscript_no: searchOptions.manuscriptNumber || '',
          subject_area: searchOptions.subjectArea || '',
          keywords: searchOptions.keywords || '',
          abstract: searchOptions.abstract || ''
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
            manuscriptsNotFound: resultsResponse['manuscripts-not-found'],
            search: resultsResponse['search']
          },
          resultsSearchOptions,
          shouldLoad: false,
          loading: false
        });
      }).catch(err => {
        console.log("error:", err);
        this.actuallyLoading = false;
        this.setState({
          results: {
            error: err
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

    this.onNodeClicked = node => {
      console.log("onNodeClicked:", node);
      this.setState({
        selectedReviewer: node.potentialReviewer
      });
    }
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
    this.props.reviewerRecommendationApi.getAllSubjectAreas().then(allSubjectAreas => this.setState({
      allSubjectAreas
    }));
    this.props.reviewerRecommendationApi.getAllKeywords().then(allKeywords => this.setState({
      allKeywords
    }));
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
      results,
      allSubjectAreas,
      allKeywords,
      selectedReviewer
    } = this.state;
    const hasPotentialReviewers =
      results && (results.potentialReviewers) && (results.potentialReviewers.length > 0);
    return (
      <View style={ styles.sceneContainer }>
        <SearchHeader
          searchOptions={ searchOptions }
          onSearchOptionsChanged={ this.onSearchOptionsChanged }
          allSubjectAreas={ allSubjectAreas }
          allKeywords={ allKeywords }
        />
        <View style={ styles.containerWithMargin } className="results-container">
          <LoadingIndicator loading={ loading }>
            <View style={ styles.resultsContainer } className="inner-results-container">
              {
                results && !hasPotentialReviewers && (
                  <SearchResult
                    searchResult={ results }
                    selectedReviewer={ selectedReviewer }
                  />
                )
              }
              {
                results && hasPotentialReviewers && (
                  <SplitPane split="vertical" defaultSize="50%">
                    <ChartResult
                      searchResult={ results }
                      onNodeClicked={ this.onNodeClicked }
                    />
                    <SearchResult
                      searchResult={ results }
                      selectedReviewer={ selectedReviewer }
                    />
                  </SplitPane>
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
