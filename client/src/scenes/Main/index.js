import React from 'react';
import { createSelector } from 'reselect';
import debounce from 'debounce';

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

class Main extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      searchOptions: {
        manuscriptNumber: '',
        keywords: ''
      },
      reqId: 0
    };

    this.getResults = createSelector(
      () => this.state.searchOptions,
      (searchOptions) => {
        if (!searchOptions.keywords && !searchOptions.manuscriptNumber) {
          return Promise.resolve({});
        }
        return this.props.reviewerRecommendationApi.recommendReviewers({
          keywords: searchOptions.keywords,
          manuscript_no: searchOptions.manuscriptNumber
        });
      }
    );

    this.updateResultsDebounced = debounce(() => {
      this.getResults().then(resultsResponse => {
        console.log("resultsResponse:", resultsResponse);
        this.setState({
          results: {
            potentialReviewers: resultsResponse['potential-reviewers'],
            matchingManuscripts: resultsResponse['matching-manuscripts']
          },
          loading: false
        });
      });
    }, 500);

    this.updateResults = () => {
      this.setState({
        loading: true
      });
      this.updateResultsDebounced();
    };
  }

  componentDidMount() {
    this.updateResults();
  }

  updateOption(state) {
    this.setState(state);
  }

  onSearchOptionsChanged = searchOptions => {
    this.setState({
      searchOptions
    });
    this.updateResults();
  }

  render() {
    const {
      loading,
      searchOptions,
      results = {}
    } = this.state;
    return (
      <View>
        <SearchHeader
          searchOptions={ searchOptions }
          onSearchOptionsChanged={ this.onSearchOptionsChanged }
        />
        <View style={ styles.containerWithMargin }>
          <LoadingIndicator loading={ loading }>
            <SearchResult searchResult={ results }/>
          </LoadingIndicator>
        </View>
      </View>
    );
  }
}

export default Main;
