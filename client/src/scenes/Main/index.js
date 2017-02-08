import React from 'react';
import { createSelector } from 'reselect';
import debounce from 'debounce';
import clipboard from 'clipboard-js';

import {
  Card,
  CardActions,
  CardHeader,
  CardText,
  Chip,
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
    },
    subSection: {
      marginBottom: 5
    },
    label: {
      display: 'inline-block',
      minWidth: 100,
      fontWeight: 'bold'
    }
  },
  manuscriptSummary: {
    container: {
      marginBottom: 10,
    },
    text: {
      fontSize: 20,
      fontWeight: 'bold'
    },
    subSection: {
      marginBottom: 5
    },
    label: {
      display: 'inline-block',
      minWidth: 100,
      fontWeight: 'bold'
    }
  },
  inlineContainer: {
    display: 'inline-block'
  },
  personChip: {
    display: 'inline-block',
    marginRight: 5
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

const combinedPersonName = person =>
  [
    person['title'],
    person['first-name'],
    person['middle-name'],
    person['last-name'],
    `(${person['person-id']}/${person['status']})`
  ].filter(s => !!s).join(' ');

const quote = s => s && `\u201c${s}\u201d`

const ManuscriptInlineSummary = ({ manuscript }) => (
  <View style={ styles.inlineContainer }>
    <Text>{ quote(manuscript['title']) }</Text>
    <Text>{ ` (${manuscript['manuscript-number']})` }</Text>
  </View>
);

const PersonInlineSummary = ({ person }) => (
  <Chip style={ styles.personChip }>
    <Text>{ combinedPersonName(person) }</Text>
  </Chip>  
);

const Membership = ({ membership }) => {
  if (membership['member-type'] != 'ORCID') {
    return (
      <Text>{ `${membership['member-type']}: ${membership['member-id']}` }</Text>
    );
  }
  return (
    <Link
      style={ styles.link }
      target="_blank"
      href={ `http://orcid.org/${membership['member-id']}` }
    >
      <Text>ORCID</Text>
    </Link>
  );
};

const formatDate = date => new Date(date).toLocaleDateString();

const formatPeriodNotAvailable = periodNotAvailable =>
  `${formatDate(periodNotAvailable['dna-start-date'])} - ${formatDate(periodNotAvailable['dna-end-date'])}`;

const PotentialReviewer = ({
  potentialReviewer: {
    person = {},
    'author-of-manuscripts': authorOfManuscripts = [],
    'reviewer-of-manuscripts': reviewerOfManuscripts = [],
    scores
  }
}) => {
  return (
    <Card style={ styles.potentialReviewer.card }>
      <CardHeader
        title={ combinedPersonName(person) }
        subtitle={ person['institution'] }
      />
      <CardText>
        {
          person.memberships && (
            <View style={ styles.potentialReviewer.subSection }>
              {
                person.memberships && person.memberships.map((membership, index) => (
                  <Membership key={ index } membership={ membership }/>
                ))
              }
            </View>
          )
        }
        {
          person['dates-not-available'] && person['dates-not-available'].length > 0 && (
            <View style={ styles.potentialReviewer.subSection }>
              <Text style={ styles.potentialReviewer.label }>Not Available: </Text>
              <Text>{ person['dates-not-available'].map(formatPeriodNotAvailable).join(', ') }</Text>
            </View>
          )
        }
        {
          person.stats && person.stats['review-duration'] && (
            <View style={ styles.potentialReviewer.subSection }>
              <Text style={ styles.potentialReviewer.label }>Review Time: </Text>
              <Text style={ styles.potentialReviewer.value }>
                { `${person.stats['review-duration']['mean'].toFixed(1)} days (avg)` }
              </Text>
            </View>
          )
        }
        <View style={ styles.potentialReviewer.subSection }>
          <Text style={ styles.potentialReviewer.label }>Author of: </Text>
          {
            authorOfManuscripts && authorOfManuscripts.map((manuscript, index) => (
              <ManuscriptInlineSummary key={ index } manuscript={ manuscript }/>
            ))
          }
        </View>
        <View  style={ styles.potentialReviewer.subSection }>
          <Text style={ styles.potentialReviewer.label }>Reviewer of: </Text>
          {
            reviewerOfManuscripts && reviewerOfManuscripts.map((manuscript, index) => (
              <ManuscriptInlineSummary key={ index } manuscript={ manuscript }/>
            ))
          }
        </View>
        <View  style={ styles.potentialReviewer.subSection }>
          <Text style={ styles.potentialReviewer.label }>Scores: </Text>
          {
            scores && (
              <Text>{ `${scores['keyword']} keyword match (higher is better)` }</Text>
            )
          }
        </View>
      </CardText>
    </Card>
  );
};

const ManuscriptSummary = ({
  manuscript: {
    title,
    'manuscript-number': manuscriptNumber,
    authors,
    reviewers
  }
}) => (
  <Card style={ styles.manuscriptSummary.container }>
    <CardHeader
      title={ quote(title) }
      subtitle={ manuscriptNumber }
    />
    <CardText>
      <View style={ styles.manuscriptSummary.subSection }>
        <Text style={ styles.manuscriptSummary.label }>Authors: </Text>
        {
          authors && authors.map((author, index) => (
            <PersonInlineSummary key={ index } person={ author }/>
          ))
        }
      </View>
      <View  style={ styles.manuscriptSummary.subSection }>
        <Text style={ styles.manuscriptSummary.label }>Reviewers: </Text>
        {
          reviewers && reviewers.map((reviewer, index) => (
            <PersonInlineSummary key={ index } person={ reviewer }/>
          ))
        }
      </View>
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
