import React from 'react';
import { createSelector } from 'reselect';
import debounce from 'debounce';
import clipboard from 'clipboard-js';
import Headroom from 'react-headroom';

import {
  Card,
  CardActions,
  CardHeader,
  CardText,
  Chip,
  Comment,
  FlatButton,
  FileInput,
  FontAwesomeIcon,
  HeaderTitle,
  Link,
  List,
  ListItem,
  LoadingIndicator,
  Paper,
  Slider,
  Text,
  TextField,
  TooltipWrapper,
  Toggle,
  View
} from '../../components';

import { range, groupBy } from '../../utils';

const KEY_NAME = 'mrkvy_file';
const KEY_DATA = 'mrkvy_data';
const KEY_SETTINGS = 'mrkvy_settings';

const commonStyles = {
  link: {
    textDecoration: 'none',
    cursor: 'hand'
  }
}

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
    marginLeft: 20
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
      marginBottom: 5,
      display: 'flex',
      flexDirection: 'row'
    },
    label: {
      display: 'inline-block',
      minWidth: 100,
      fontWeight: 'bold'
    },
    value: {
      flex: 1
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
  tooltipContent: {
    header: {
      margin: 0
    },
    label: {
      fontWeight: 'bold'
    },
    abstract: {
      marginTop: 5
    }
  },
  inlineContainer: {
    display: 'inline-block'
  },
  personChip: {
    display: 'inline-block',
    marginRight: 5
  },
  flexColumn: {
    display: 'flex',
    flexDirection: 'column'
  },
  flexRow: {
    display: 'flex',
    flexDirection: 'row'
  },
  unrecognisedMembership: {
    display: 'inline-block',
    marginLeft: 10
  },
  membershipLink: {
    ...commonStyles.link,
    display: 'inline-block',
    marginLeft: 10
  },
  manuscriptInlineSummary: {
    matchingSubjectAreas: {
      display: 'inline-block'
    },
    notMatchingSubjectAreas: {
      display: 'inline-block',
      color: '#888'
    }
  },
  containerWithMargin: {
    margin: 8
  },
  header: {
    padding: 8,
    paddingTop: 0,
    backgroundColor: '#fff',
    marginTop: -10,
    overflow: 'hidden'
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
    person['is-early-career-reviewer'] ? '(ECR)': undefined,
    person['status'] !== 'Active' && `(${person['status']})`
  ].filter(s => !!s).join(' ');

const quote = s => s && `\u201c${s}\u201d`

const ManuscriptTooltipContent = ({
  manuscript: { title, abstract, 'subject-areas': subjectAreas }
}) => (
  <View>
    <HeaderTitle style={ styles.tooltipContent.header }>{ title }</HeaderTitle>
    <View>
      <Text style={ styles.tooltipContent.label }>{ 'Subject Areas: ' }</Text>
      <Text>{ subjectAreas.join(', ')}</Text>
    </View>
    <View style={ styles.tooltipContent.abstract }>
      <Text>{ abstract }</Text>
    </View>
  </View>
)

const formatManuscriptId = manuscript =>
  `${manuscript['manuscript-no']} v${manuscript['version-no']}`

const formatKeywordScoreInline = keyword =>
  keyword ? keyword + ' keyword match' : '';

const formatSimilarityScoreInline = similarity =>
  similarity ? similarity.toFixed(2) + ' similarity' : '';

const formatScoresInline = ({ keyword, similarity }) =>
  [
    formatKeywordScoreInline(keyword),
    formatSimilarityScoreInline(similarity)
  ].filter(s => !!s).join(', ');

const hasMatchingSubjectAreas = (manuscript, requestedSubjectAreas) =>
  requestedSubjectAreas.length === 0 || !!manuscript['subject-areas'].filter(
    subjectArea => requestedSubjectAreas.has(subjectArea)
  )[0];

const ManuscriptInlineSummary = ({ manuscript, scores = {}, requestedSubjectAreas }) => (
  <View
    style={
      hasMatchingSubjectAreas(manuscript, requestedSubjectAreas) ?
      styles.manuscriptInlineSummary.matchingSubjectAreas :
      styles.manuscriptInlineSummary.notMatchingSubjectAreas
    }
  >
    <TooltipWrapper content={ <ManuscriptTooltipContent manuscript={ manuscript}/> } style={ styles.inlineContainer }>
      <Text>{ quote(manuscript['title']) }</Text>
    </TooltipWrapper>
    <Text>{ ` (${formatManuscriptId(manuscript)})` }</Text>
    <Text>{ ` - ${formatScoresInline(scores)}` }</Text>
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
      <Text style={ styles.unrecognisedMembership }>
        { `${membership['member-type']}: ${membership['member-id']}` }
      </Text>
    );
  }
  return (
    <View style={ styles.inlineContainer }>
      <Link
        style={ styles.membershipLink }
        target="_blank"
        href={ `http://orcid.org/${membership['member-id']}` }
      >
        <Text>ORCID</Text>
      </Link>
      <Link
        style={ styles.membershipLink }
        target="_blank"
        href={ `http://search.crossref.org/?q=${membership['member-id']}` }
      >
        <Text>Crossref</Text>
      </Link>
    </View>
  );
};

const personFullName = person => [
  person['first-name'],
  person['middle-name'],
  person['last-name']
].filter(s => !!s).join(' ');

const PersonWebSearchLink = ({ person }) => (
  <Link
    style={ styles.membershipLink }
    target="_blank"
    href={ `http://search.crossref.org/?q=${personFullName(person)}` }
  >
    <Text>Crossref</Text>
  </Link>
);

const formatDate = date => new Date(date).toLocaleDateString();

const formatPeriodNotAvailable = periodNotAvailable =>
  `${formatDate(periodNotAvailable['dna-start-date'])} - ${formatDate(periodNotAvailable['dna-end-date'])}`;

const PotentialReviewer = ({
  potentialReviewer: {
    person = {},
    'author-of-manuscripts': authorOfManuscripts = [],
    'reviewer-of-manuscripts': reviewerOfManuscripts = [],
    scores
  },
  requestedSubjectAreas
}) => {
  const manuscriptScoresByManuscriptNo = groupBy(scores['by-manuscript'] || [], s => s['manuscript-no']);
  const memberships = person.memberships || [];
  const membershipComponents = memberships.map((membership, index) => (
    <Membership key={ index } membership={ membership }/>
  ));
  if (membershipComponents.length === 0) {
    membershipComponents.push((<PersonWebSearchLink key="search" person={ person }/>));
  }
  const titleComponent = (
    <View style={ styles.inlineContainer }>
      <Text>{ combinedPersonName(person) }</Text>
      { membershipComponents }
    </View>
  );
  const renderManuscripts = manuscripts => manuscripts && manuscripts.map((manuscript, index) => (
    <ManuscriptInlineSummary
      key={ index }
      manuscript={ manuscript }
      scores={ manuscriptScoresByManuscriptNo[manuscript['manuscript-no']] }
      requestedSubjectAreas={ requestedSubjectAreas }
    />
  ));
  return (
    <Card style={ styles.potentialReviewer.card }>
      <Comment text={ `Person id: ${person['person-id']}` }/>
      <CardHeader
        title={ titleComponent }
        subtitle={ person['institution'] }
      />
      <CardText>
        {
          person['dates-not-available'] && person['dates-not-available'].length > 0 && (
            <View style={ styles.potentialReviewer.subSection }>
              <Text style={ styles.potentialReviewer.label }>Not Available: </Text>
              <Text style={ styles.potentialReviewer.value }>
                { person['dates-not-available'].map(formatPeriodNotAvailable).join(', ') }
              </Text>
            </View>
          )
        }
        {
          person.stats && person.stats['review-duration'] && (
            <View style={ styles.potentialReviewer.subSection }>
              <Text style={ styles.potentialReviewer.label }>Review Time: </Text>
              <View style={ styles.potentialReviewer.value }>
                <Text>
                  { `${person.stats['review-duration']['mean'].toFixed(1)} days
                    (avg over ${person.stats['review-duration']['count']} reviews)` }
                </Text>
                {
                  person.stats['review-duration-12m'] && (
                    <Text>
                      { `, with ${person.stats['review-duration-12m']['count']}
                        review(s) within the last 12 months
                        (avg ${person.stats['review-duration-12m']['mean'].toFixed(1)} days)` }
                    </Text>
                  )
                }
              </View>
            </View>
          )
        }
        <View style={ styles.potentialReviewer.subSection }>
          <Text style={ styles.potentialReviewer.label }>Author of: </Text>
          <View style={ styles.potentialReviewer.value }>
            <FlexColumn>
              { renderManuscripts(authorOfManuscripts) }
            </FlexColumn>
          </View>
        </View>
        <View  style={ styles.potentialReviewer.subSection }>
          <Text style={ styles.potentialReviewer.label }>Reviewer of: </Text>
          <View style={ styles.potentialReviewer.value }>
            <FlexColumn>
              { renderManuscripts(reviewerOfManuscripts) }
            </FlexColumn>
          </View>
        </View>
        <View  style={ styles.potentialReviewer.subSection }>
          <Text style={ styles.potentialReviewer.label }>Scores: </Text>
          <View style={ styles.potentialReviewer.value }>
            <FlexColumn>
              {
                (scores && scores['keyword'] && (
                  <Text>{ `${scores['keyword'].toFixed(2)} keyword match (higher is better)` }</Text>
                )) || null
              }
              {
                (scores && scores['similarity'] && (
                  <Text>{ `${scores['similarity'].toFixed(2)} similarity (max across articles)` }</Text>
                )) || null
              }
            </FlexColumn>
          </View>
        </View>
      </CardText>
    </Card>
  );
};


const ManuscriptSummary = ({
  manuscript: {
    title,
    'manuscript-no': manuscriptNo,
    'version-no': versionNo,
    abstract,
    authors,
    reviewers,
    'subject-areas': subjectAreas
  }
}) => (
  <Card style={ styles.manuscriptSummary.container } initiallyExpanded={ true }>
    <CardHeader
      title={ quote(title) }
      subtitle={ `${manuscriptNo} v${versionNo}` }
      actAsExpander={ true }
      showExpandableButton={ true }
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
    <CardText expandable={ true }>
      <View  style={ styles.manuscriptSummary.subSection }>
        <Text style={ styles.manuscriptSummary.label }>Subject areas:</Text>
        <Text>{ subjectAreas.join(', ') }</Text>
      </View>
      <View  style={ styles.manuscriptSummary.subSection }>
        <FlexColumn>
          <Text style={ styles.manuscriptSummary.label }>Abstract:</Text>
          <Text>{ quote(abstract) }</Text>
        </FlexColumn>
      </View>
    </CardText>
  </Card>
);

const FlexColumn = props => (
  <View style={ styles.flexColumn }>
    { props.children }
  </View>
);

const FlexRow = props => (
  <View style={ styles.flexRow }>
    { props.children }
  </View>
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

  extractAllSubjectAreas(manuscripts) {
    const subjectAreas = new Set();
    if (manuscripts) {
      manuscripts.forEach(m => {
        m['subject-areas'].forEach(subjectArea => {
          subjectAreas.add(subjectArea);
        })
      });
    };
    return subjectAreas;
  }

  render() {
    const {
      loading,
      searchOptions,
      results = {}
    } = this.state;
    const { manuscriptNumber, keywords } = searchOptions;
    const { potentialReviewers = [], matchingManuscripts = [] } = results;
    const requestedSubjectAreas = this.extractAllSubjectAreas(matchingManuscripts);
    return (
      <View>
        <Headroom>
          <Paper>
            <View style={ styles.header }>
              <FlexRow>
                <View style={ styles.inlineContainer }>
                  <FontAwesomeIcon style={{ paddingTop: 40 }} name="search"/>
                </View>
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
              </FlexRow>
            </View>
          </Paper>
        </Headroom>
        <View style={ styles.containerWithMargin }>
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
                        requestedSubjectAreas={ requestedSubjectAreas }
                      />
                    ))
                  }
                </View>
              </LoadingIndicator>
            </CardText>
          </Card>
        </View>
      </View>
    );
  }
}

export default Main;
