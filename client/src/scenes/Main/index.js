import React from 'react';
import { createSelector } from 'reselect';
import debounce from 'debounce';
import clipboard from 'clipboard-js';

import {
  Card,
  CardActions,
  CardHeader,
  CardText,
  FlatButton,
  FileInput,
  FontAwesomeIcon,
  Link,
  List,
  ListItem,
  LoadingIndicator,
  Slider,
  Text,
  TextField,
  Toggle,
  View
} from '../../components';

import { range } from '../../utils';

const KEY_NAME = 'mrkvy_file';
const KEY_DATA = 'mrkvy_data';
const KEY_SETTINGS = 'mrkvy_settings';

const styles = {
  card: {
    marginBottom: 20
  },
  cardHeader: {
    backgroundColor: '#eee',
    fontWeight: 'bold'
  },
  controlPanel: {
    display: 'flex'
  },
  step: {
    maxWidth: 400,
    display: 'inline-block',
    marginRight: 10
  },
  field: {
    marginBottom: 10
  },
  slider: {
    container: {
      marginTop: 30
    },
    label: {
    },
    slider: {
    }
  },
  info: {
    marginTop: 10
  },
  stats: {
    container: {
    },
    label: {
      display: 'inline-block',
      minWidth: 100,
      fontWeight: 'bold'
    },
    value: {
      display: 'inline-block',
      textAlign: 'right',
      minWidth: 100
    }
  },
  paragraph: {
    marginBottom: 10
  },
  link: {
    textDecoration: 'none',
    cursor: 'hand'
  },
  potentialReviewer: {
    container: {
      fontSize: 20,
      padding: 5,
      borderWidth: 1,
      borderColor: '#eee',
      borderStyle: 'solid',
      margin: 3
    },
    card: {
      marginBottom: 10,
    }
  },
  manuscriptSummary: {
    container: {
      marginBottom: 10,
    },
    text: {
      fontSize: 20,
      fontWeight: 'bold'
    }
  }
}

const LabelledSlider = ({ label, ...otherProps }) => (
  <View style={ styles.slider.container }>
    <Text style={ styles.slider.label }>{ label }</Text>
    <Slider style={ styles.slider.slider } { ...otherProps }/>
  </View>
);

const LabelledStats = ({ label, value }) => (
  <View style={ styles.stats.container }>
    <Text style={ styles.stats.label }>{ `${label}: ` }</Text>
    <Text style={ styles.stats.value }>{ value }</Text>
  </View>
);

const combinedReviewerName = person =>
  [
    person['title'],
    person['first-name'],
    person['middle-name'],
    person['last-name']
  ].filter(s => !!s).join(' ');

const ManuscriptInlineSummary = ({ manuscript }) => (
  <Text>{ manuscript['manuscript-number'] }</Text>
);

const PotentialReviewer = ({
  potentialReviewer: {
    person = {},
    'author-of-manuscripts': authorOfManuscripts = [],
    'reviewer-of-manuscripts': reviewerOfManuscripts = []
  }
}) => {
  return (
    <Card style={ styles.potentialReviewer.card }>
      <CardHeader
        title={ combinedReviewerName(person) }
        subtitle={ person['institution'] }
      />
      <CardText>
        <Text>Author of: </Text>
        {
          authorOfManuscripts && authorOfManuscripts.map((manuscript, index) => (
            <ManuscriptInlineSummary manuscript={ manuscript }/>
          ))
        }
      </CardText>
      <CardText>
        <Text>Reviewer of: </Text>
        {
          reviewerOfManuscripts && reviewerOfManuscripts.map((manuscript, index) => (
            <ManuscriptInlineSummary manuscript={ manuscript }/>
          ))
        }
      </CardText>
    </Card>
  );
};

const ManuscriptSummary = ({ manuscript }) => (
  <Card style={ styles.manuscriptSummary.container }>
    <CardText>
      <Text style={ styles.manuscriptSummary.text }>{ manuscript['manuscript-number'] }</Text>
    </CardText>
  </Card>
);

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

  updateSearchOption(key, value) {
    this.setState(state => ({
      searchOptions: {
        ...state.searchOptions,
        [key]: value
      }
    }));
    this.updateResults();
  }

  updateOption(state) {
    this.setState(state);
  }

  render() {
    const {
      loading,
      searchOptions,
      results = {}
    } = this.state;
    const { manuscriptNumber, keywords } = searchOptions;
    const { potentialReviewers = [], matchingManuscripts = [] } = results;
    return (
      <View>
        <Card style={ styles.card } initiallyExpanded={ true }>
          <CardHeader
            style={ styles.cardHeader }
            title="Find reviewers"
            actAsExpander={ true }
            showExpandableButton={ true }
          />
          <CardText style={ styles.controlPanel } expandable={ true }>
            <View style={ styles.step }>
              <View style={ styles.field }>
                <TextField
                  floatingLabelText="Manuscript number"
                  value={ manuscriptNumber }
                  onChange={ (event, newValue) => this.updateSearchOption('manuscriptNumber', newValue) }
                  style={ styles.textField }
                />
              </View>
              <View style={ styles.field }>
                <TextField
                  floatingLabelText="Keywords (comma separated)"
                  value={ keywords }
                  onChange={ (event, newValue) => this.updateSearchOption('keywords', newValue) }
                  style={ styles.textField }
                />
              </View>
            </View>
          </CardText>
        </Card>
        <Card style={ styles.card } initiallyExpanded={ true }>
          <CardHeader
            style={ styles.cardHeader }
            title="Results"
            actAsExpander={ true }
            showExpandableButton={ true }
          />
          <CardText expandable={ true }>
            <LoadingIndicator loading={ loading }>
              <View>
                {
                  matchingManuscripts && matchingManuscripts.map((matchingManuscript, index) => (
                    <ManuscriptSummary
                      key={ index }
                      manuscript={ matchingManuscript }
                    />
                  ))
                }
                {
                  potentialReviewers && potentialReviewers.map((potentialReviewer, index) => (
                    <PotentialReviewer
                      key={ index }
                      potentialReviewer={ potentialReviewer }
                    />
                  ))
                }
              </View>
            </LoadingIndicator>
          </CardText>
        </Card>
      </View>
    );
  }
}

export default Main;
