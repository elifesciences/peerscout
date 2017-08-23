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

import {
  reportError
} from '../../monitoring';

import {
  Auth,
  NullAuth,
  LoggedInIndicator,
  LoginForm
} from '../../auth';

import AppLoading from './AppLoading';
import SearchHeader from './SearchHeader';
import SearchResult from './SearchResult';
import ChartResult from './ChartResult';
import Help from './Help';

const styles = {
  appLoading: {
    flex: 1,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center'
  },
  loggedInIndicator: {
    position: 'absolute',
    right: 0,
    zIndex: 10,
    padding: 5,
    color: '#fff'
  },
  loginForm: {
    flex: 1,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center'
  },
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
};

const HELP_OPEN_KEY = 'helpOpen';
const LEGEND_OPEN_KEY = 'legendOpen';

const getBooleanLocalStorageItem = (key, defaultValue) => {
  const value = localStorage.getItem(key);
  return value === 'true' ? true :
    (value === 'false' ? false : defaultValue);
};

const saveLocalStorageItem = (key, value) => {
  window.setTimeout(() => localStorage.setItem(key, '' + value), 1);
};

class Main extends React.Component {
  constructor(props) {
    super(props);
    this.history = createHashHistory({});
    this.defaultSearchOptions = {
      manuscriptNumber: '',
      keywords: ''
    };
    this.defaultConfig = {
      showAllRelatedManuscripts: true,
      maxRelatedManuscripts: 15
    };
    this.state = {
      searchOptions: this.defaultSearchOptions,
      reqId: 0,
      helpOpen: getBooleanLocalStorageItem(HELP_OPEN_KEY, true),
      legendOpen: getBooleanLocalStorageItem(LEGEND_OPEN_KEY, true)
    };

    this.getResults = createSelector(
      [
        () => this.state.searchOptions,
        () => this.state.authenticationState
      ],
      (searchOptions, authenticationState) => {
        if (
          !authenticationState.authenticated ||
          (
            !searchOptions.manuscriptNumber &&
            !(searchOptions.subjectArea || searchOptions.keywords)
          )
        ) {
          return Promise.resolve();
        }
        return this.props.reviewerRecommendationApi.recommendReviewers({
          manuscript_no: searchOptions.manuscriptNumber || '',
          subject_area: searchOptions.subjectArea || '',
          keywords: searchOptions.keywords || '',
          abstract: searchOptions.abstract || '',
          limit: searchOptions.limit || '50',
        }, {
          headers: {
            access_token: authenticationState && authenticationState.access_token
          }
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
      }).catch(error => {
        reportError("failed to fetch results", error);
        const notAuthorized = this.props.reviewerRecommendationApi.isNotAuthorizedError(error);
        this.actuallyLoading = false;
        this.setState({
          results: {
            error,
            notAuthorized
          },
          resultsSearchOptions,
          shouldLoad: false,
          loading: false
        });
        if (notAuthorized && this.auth) {
          this.auth.revalidateToken();
        }
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
        this.defaultConfig.showAllRelatedManuscripts,
      maxRelatedManuscripts:
        configResult.max_related_manuscripts != undefined ?
        configResult.max_related_manuscripts :
        this.defaultConfig.maxRelatedManuscripts,
      auth0_domain: configResult.auth0_domain,
      auth0_client_id: configResult.auth0_client_id
    }
  }

  initConfig(config) {
    if (config.auth0_domain && config.auth0_client_id) {
      this.auth = new Auth({
        domain: config.auth0_domain,
        client_id: config.auth0_client_id
      });
      this.auth.initialise();
    } else {
      this.auth = new NullAuth();
    }
    this.setState({
      config,
      authenticationState: this.auth.getAuthenticationState()
    });
    this.auth.onStateChange(authenticationState => {
      this.setState({
        authenticationState
      });
    });
    this.updateSearchOptionsFromLocation(this.history.location);
    this.unlisten = this.history.listen((location, action) => {
      this.updateSearchOptionsFromLocation(location);
    });
  }

  componentDidMount() {
    this.props.reviewerRecommendationApi.getConfig().then(config => this.initConfig(
      this.translateConfig(config)
    )).catch(err => {
      reportError('failed to fetch config', err);
    });
    this.props.reviewerRecommendationApi.getAllSubjectAreas().then(allSubjectAreas => this.setState({
      allSubjectAreas
    })).catch(err => {
      reportError('failed to fetch subject areas', err);
    });
    this.props.reviewerRecommendationApi.getAllKeywords().then(allKeywords => this.setState({
      allKeywords
    })).catch(err => {
      reportError('failed to fetch keywords', err);
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

  setHelpOpen(helpOpen) {
    this.setState({helpOpen});
    saveLocalStorageItem(HELP_OPEN_KEY, helpOpen);
  }

  onCloseHelp = () => {
    this.setHelpOpen(false);
  }

  onOpenHelp = () => {
    this.setHelpOpen(true);
  }

  setLegendOpen(legendOpen) {
    this.setState({legendOpen});
    saveLocalStorageItem(LEGEND_OPEN_KEY, legendOpen);
  }

  onCloseLegend = () => {
    this.setLegendOpen(false);
  }

  onOpenLegend = () => {
    this.setLegendOpen(true);
  }

  onSelectPotentialReviewer = potentialReviewer => {
    this.setState({
      selectedNode: null,
      selectedReviewer: potentialReviewer,
      selectedManuscript: null
    });
  }

  render() {
    const {
      config,
      loading,
      searchOptions,
      results,
      allSubjectAreas,
      allKeywords,
      selectedNode,
      selectedReviewer,
      selectedManuscript,
      helpOpen,
      legendOpen,
      authenticationState
    } = this.state;
    if (!config) {
      return (<AppLoading style={ styles.appLoading }/>);
    }
    const {
      showAllRelatedManuscripts,
      maxRelatedManuscripts
    } = config;
    const hasPotentialReviewers =
      results && (results.potentialReviewers) && (results.potentialReviewers.length > 0);
    let content;
    let loggedInIndicator = null;
    if (!authenticationState.authenticated && !authenticationState.authenticating) {
      content = (
        <LoginForm auth={ this.auth } style={ styles.loginForm }/>
      );
    } else {
      if (authenticationState.logged_in) {
        loggedInIndicator = (
          <LoggedInIndicator style={ styles.loggedInIndicator } auth={ this.auth }/>
        );
      }
      content = (
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
                  selectedReviewer={ selectedReviewer }
                  showAllRelatedManuscripts={ showAllRelatedManuscripts }
                  maxRelatedManuscripts={ maxRelatedManuscripts }
                  legendOpen={ legendOpen }
                  onOpenLegend={ this.onOpenLegend }
                  onCloseLegend={ this.onCloseLegend }
                />
                <SearchResult
                  searchResult={ results }
                  selectedReviewer={ selectedReviewer }
                  selectedManuscript={ selectedManuscript }
                  onClearSelection={ this.onClearSelection }
                  onSelectPotentialReviewer={ this.onSelectPotentialReviewer }
                />
              </SplitPane>
            )
          }
        </FlexRow>
      );
    }
    return (
      <FlexColumn>
        { loggedInIndicator }
        {
          authenticationState.authenticated && (
            <SearchHeader
              searchOptions={ searchOptions }
              onSearchOptionsChanged={ this.onSearchOptionsChanged }
              allSubjectAreas={ allSubjectAreas }
              allKeywords={ allKeywords }
            />
          )
        }
        <FlexRow style={ styles.outerResultsContainer } className="results-container">
          <LoadingIndicator style={ styles.loadingIndicator } loading={ loading || authenticationState.authenticating }>
            { content }
          </LoadingIndicator>
        </FlexRow>
        {
          authenticationState.authenticated && (
            <Help
              open={ helpOpen }
              onClose={ this.onCloseHelp }
              onOpen={ this.onOpenHelp }
            />
          )
        }
      </FlexColumn>
    );
  }
}

export default Main;
