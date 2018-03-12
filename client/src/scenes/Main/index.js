import React from 'react';
import { createSelector } from 'reselect';
import debounce from 'debounce';
import SplitPane from 'react-split-pane';
import Radium from 'radium';

import {
  FlexColumn,
  FlexRow,
  LoadingIndicator,
  View,
  withHashHistory,
  withLocalStorage
} from '../../components';

import {
  Auth,
  NullAuth,
  LoggedInIndicator,
  LoginForm,
  withAuthenticatedAuthenticationState
} from '../../auth';

import AppLoading from './AppLoading';
import SearchHeader from './SearchHeader';
import SearchResult from './SearchResult';
import ChartResult from './ChartResult';
import Help from './Help';

import { withLoadedConfig } from './withConfig';
import { withLoadedSearchTypes } from './withSearchTypes';
import { withLoadedAllSubjectAreas } from './withAllSubjectAreas';
import { withLoadedAllKeywords } from './withAllKeywords';
import { withSearchOptions } from './withSearchOptions';
import { withDebouncedSearchResults } from './withSearchResults';

const styles = {
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

const HELP_OPEN_KEY = 'helpOpen';
const LEGEND_OPEN_KEY = 'legendOpen';

const getBooleanLocalStorageItem = (storage, key, defaultValue) => {
  const value = storage.getItem(key);
  return value === 'true' ? true :
    (value === 'false' ? false : defaultValue);
};

const saveLocalStorageItem = (storage, key, value) => {
  window.setTimeout(() => storage.setItem(key, '' + value), 1);
};

export class MainView extends React.Component {
  constructor(props) {
    super(props);

    const { config, searchTypes } = props;

    this.defaultConfig = {
      showAllRelatedManuscripts: true,
      maxRelatedManuscripts: 15
    };
    this.state = {
      config,
      reqId: 0,
      helpOpen: getBooleanLocalStorageItem(this.props.localStorage, HELP_OPEN_KEY, true),
      legendOpen: getBooleanLocalStorageItem(this.props.localStorage, LEGEND_OPEN_KEY, true),
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

  updateOption(state) {
    this.setState(state);
  }

  onSearchOptionsChanged = searchOptions => {
    this.props.setSearchOptions(searchOptions);
  }

  setHelpOpen(helpOpen) {
    this.setState({helpOpen});
    saveLocalStorageItem(this.props.localStorage, HELP_OPEN_KEY, helpOpen);
  }

  onCloseHelp = () => {
    this.setHelpOpen(false);
  }

  onOpenHelp = () => {
    this.setHelpOpen(true);
  }

  setLegendOpen(legendOpen) {
    this.setState({legendOpen});
    saveLocalStorageItem(this.props.localStorage, LEGEND_OPEN_KEY, legendOpen);
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
      allSubjectAreas,
      allKeywords,
      authenticationState,
      searchOptions,
      searchResults,
      searchTypes,
      ...otherProps
    } = this.props;
    const {
      config,
      selectedNode,
      selectedReviewer,
      selectedManuscript,
      helpOpen,
      legendOpen
    } = this.state;
    const {
      showAllRelatedManuscripts,
      maxRelatedManuscripts
    } = config;
    const context = {
      ...otherProps,
      authenticationState
    };
    const results = searchResults.value;
    const hasPotentialReviewers =
      results && (results.potentialReviewers) && (results.potentialReviewers.length > 0);
    let content;
    let loggedInIndicator = null;
    if (authenticationState.logged_in) {
      loggedInIndicator = (
        <LoggedInIndicator auth={ this.props.auth } style={ styles.loggedInIndicator }/>
      );
    }
    content = (
      <FlexRow style={ styles.resultsContainer } className="inner-results-container">
        {
          (results || searchResults.error) && !hasPotentialReviewers && (
            <SearchResult
              { ...context }
              searchResult={ results }
              error={ searchResults.error }
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
                { ...context }
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
    return (
      <FlexColumn>
        { loggedInIndicator }
        {
          <SearchHeader
            searchOptions={ searchOptions }
            onSearchOptionsChanged={ this.onSearchOptionsChanged }
            allSubjectAreas={ allSubjectAreas }
            allKeywords={ allKeywords }
            searchTypes={ searchTypes }
          />
        }
        <FlexRow style={ styles.outerResultsContainer } className="results-container">
          <LoadingIndicator style={ styles.loadingIndicator } loading={ searchResults.loading }>
            { content }
          </LoadingIndicator>
        </FlexRow>
        {
          <Help
            open={ helpOpen }
            onClose={ this.onCloseHelp }
            onOpen={ this.onOpenHelp }
          />
        }
      </FlexColumn>
    );
  }
}

export const Main = withLocalStorage(withLoadedConfig(
  withAuthenticatedAuthenticationState(
    withLoadedAllSubjectAreas(
      withLoadedAllKeywords(
        withLoadedSearchTypes(
          withHashHistory(
            withSearchOptions(
              withDebouncedSearchResults(
                MainView
              )
            )
          )
        )
      )
    )
  )
));

export default Main;
