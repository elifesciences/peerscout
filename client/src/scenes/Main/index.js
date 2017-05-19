import React from 'react';
import { createSelector } from 'reselect';
import debounce from 'debounce';
import createHashHistory from 'history/createHashHistory';
import equals from 'deep-equal';
import SplitPane from 'react-split-pane';
import Radium from 'radium';

import {
  FlexColumn,
  FlexRow,
  LoadingIndicator,
  View
} from '../../components';

import SearchHeader from './SearchHeader';
import SearchResult from './SearchResult';
import ChartResult from './ChartResult';
import Help from './Help';

const styles = {
  outerResultsContainer: {
    flex: 1
  },
  resultsContainer: {
    position: 'relative',
    flex: 1
  },
  splitPane: {
    display: 'flex',
    flex: 1
  },
  loadingIndicator: {
    position: 'absolute',
    marginTop: 10,
    marginLeft: 10
  }
};

const RadiumSplitPane = Radium(SplitPane);

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
    this.defaultConfig = {
      showAllRelatedManuscripts: true
    };
    this.state = {
      searchOptions: this.defaultSearchOptions,
      reqId: 0,
      config: this.defaultConfig
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
          abstract: searchOptions.abstract || '',
          limit: searchOptions.limit || '100'
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
            potentialReviewers: resultsResponse['potential_reviewers'],
            matchingManuscripts: resultsResponse['matching_manuscripts'],
            manuscriptsNotFound: resultsResponse['manuscripts_not_found'],
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
        selectedNode: node.potentialReviewer || node.manuscript ? node : null,
        selectedReviewer: node.potentialReviewer,
        selectedManuscript: node.manuscript
      });
    };

    this.onClearSelection = () => {
      this.setState({
        selectedNode: null,
        selectedReviewer: null,
        selectedManuscript: null
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

  translateConfig(configResult) {
    return {
      showAllRelatedManuscripts:
        configResult.chart_show_all_manuscripts != undefined ?
        configResult.chart_show_all_manuscripts == 'true' :
        this.defaultConfig.showAllRelatedManuscripts
    }
  }

  componentDidMount() {
    this.updateSearchOptionsFromLocation(this.history.location);
    this.unlisten = this.history.listen((location, action) => {
      this.updateSearchOptionsFromLocation(location);
    });
    this.props.reviewerRecommendationApi.getConfig().then(config => this.setState({
      config: this.translateConfig(config)
    }));
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
      config: {
        showAllRelatedManuscripts
      },
      loading,
      searchOptions,
      results,
      allSubjectAreas,
      allKeywords,
      selectedNode,
      selectedReviewer,
      selectedManuscript
    } = this.state;
    const hasPotentialReviewers =
      results && (results.potentialReviewers) && (results.potentialReviewers.length > 0);
    return (
      <FlexColumn>
        <SearchHeader
          searchOptions={ searchOptions }
          onSearchOptionsChanged={ this.onSearchOptionsChanged }
          allSubjectAreas={ allSubjectAreas }
          allKeywords={ allKeywords }
        />
        <FlexRow style={ styles.outerResultsContainer } className="results-container">
          <LoadingIndicator style={ styles.loadingIndicator } loading={ loading }>
            <FlexRow style={ styles.resultsContainer } className="inner-results-container">
              {
                results && !hasPotentialReviewers && (
                  <SearchResult
                    searchResult={ results }
                    selectedReviewer={ selectedReviewer }
                    selectedManuscript={ selectedManuscript }
                    onClearSelection={ this.onClearSelection }
                  />
                )
              }
              {
                results && hasPotentialReviewers && (
                  <SplitPane style={ styles.splitPane } split="vertical" defaultSize="50%">
                    <ChartResult
                      searchResult={ results }
                      onNodeClicked={ this.onNodeClicked }
                      selectedNode={ selectedNode }
                      showAllRelatedManuscripts={ showAllRelatedManuscripts }
                    />
                    <SearchResult
                      searchResult={ results }
                      selectedReviewer={ selectedReviewer }
                      selectedManuscript={ selectedManuscript }
                      onClearSelection={ this.onClearSelection }
                    />
                  </SplitPane>
                )
              }
            </FlexRow>
          </LoadingIndicator>
        </FlexRow>
        <Help/>
      </FlexColumn>
    );
  }
}

export default Main;
