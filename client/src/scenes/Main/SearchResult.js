import React from 'react';
import More from 'react-more';

import {
  Card,
  CardActions,
  CardHeader,
  CardText,
  Chip,
  Comment,
  FlatButton,
  FlexColumn,
  FontAwesomeIcon,
  InlineContainer,
  Link,
  RaisedButton,
  Text,
  TooltipWrapper,
  View
} from '../../components';

import { groupBy } from '../../utils';

import ManuscriptTooltipContent from './ManuscriptTooltipContent';

import {
  formatCombinedScore,
  formatScoreWithDetails
} from './formatUtils';

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
  inlineContainer: {
    display: 'inline-block'
  },
  personChip: {
    display: 'inline-block',
    marginRight: 5
  },
  unrecognisedMembership: {
    display: 'inline-block',
    marginLeft: 10
  },
  emailLink: {
    ...commonStyles.link,
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
  errorMessage: {
    padding: 20,
    fontSize: 20,
    color: '#f22'
  },
  buttons: {
    padding: 10
  }
}

const formatPersonStatus = status =>
  status && status.length > 0 ? status : 'Unknown status';

const combinedPersonName = person =>
  [
    person['title'],
    person['first-name'],
    person['middle-name'],
    person['last-name'],
    person['is-early-career-researcher'] ? '(early career researcher)': undefined,
    person['status'] !== 'Active' && `(${formatPersonStatus(person['status'])})`
  ].filter(s => !!s).join(' ');

const quote = s => s && `\u201c${s}\u201d`

const formatManuscriptId = manuscript => manuscript['manuscript-no'];

const doiUrl = doi => doi && 'http://dx.doi.org/' + doi;

const hasMatchingSubjectAreas = (manuscript, requestedSubjectAreas) =>
  requestedSubjectAreas.length === 0 || !!(manuscript['subject-areas'] || []).filter(
    subjectArea => requestedSubjectAreas.has(subjectArea)
  )[0];

const Score = ({ score = {} }) => (
  <Text
    className="score"
    title={ formatScoreWithDetails(score) }
  >{ formatCombinedScore(score.combined) }</Text>
);

const ManuscriptRefLink = ({ manuscript }) => (
  <Link
    style={ styles.manuscriptLink }
    target="_blank"
    href={ doiUrl(manuscript['doi']) }
  >
    <Text>{ formatManuscriptId(manuscript) }</Text>
  </Link>
);

const ManuscriptInlineSummary = ({ manuscript, scores = {}, requestedSubjectAreas }) => {
  return (
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
      <Text>{ ' ' }</Text>
      <Text>{ formatDate(manuscript['published-date']) }</Text>
      <Text>{ ' (' }</Text>
      <ManuscriptRefLink manuscript={ manuscript }/>
      <Text>{ ') ' }</Text>
      {
        scores.combined && (
          <InlineContainer>
            <Text>{ '- ' }</Text>
            <Score score={ scores }/>
          </InlineContainer>
        ) || null
      }
    </View>
  );
};

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
    href={ `http://search.crossref.org/?q=${encodeURIComponent(personFullName(person))}` }
  >
    <Text><FontAwesomeIcon name="search"/></Text>
  </Link>
);

const PersonEmailLink = ({ person: { email } }) => (
  <Link
    style={ styles.emailLink }
    target="_blank"
    href={ `mailto:${email}` }
  >
    <Text><FontAwesomeIcon name="envelope"/></Text>
  </Link>
);

const formatDate = date => date && new Date(date).toLocaleDateString();

const formatPeriodNotAvailable = periodNotAvailable =>
  `${formatDate(periodNotAvailable['dna-start-date'])} - ${formatDate(periodNotAvailable['dna-end-date'])}`;

const formatCount = (count, singular, plural, suffix) =>
  (count !== undefined) && `${count} ${count === 1 ? singular : plural} ${suffix || ''}`.trim();

const formatDays = days =>
  (days !== undefined) && `${days.toFixed(1)} ${days === 1.0 ? 'day' : 'days'}`;

const formatPeriodStats = periodStats => {
  const {
    mean,
    count
  } = periodStats['review-duration'] || {};
  return [
    mean && `${formatDays(mean)} (avg over ${formatCount(count, 'review', 'reviews')})`,
    formatCount(periodStats['reviews-in-progress'], 'review', 'reviews', 'in progress'),
    formatCount(periodStats['waiting-to-be-accepted'], 'review', 'reviews', 'awaiting response'),
    formatCount(periodStats['declined'], 'review', 'reviews', 'declined')
  ].filter(s => !!s).join(', ');
}

const renderStats = stats => {
  const overallStats = formatPeriodStats((stats || {})['overall'] || {});
  const last12mStats = formatPeriodStats((stats || {})['last-12m'] || {});
  if (!overallStats && !last12mStats) {
    return;
  }
  return (
    <FlexColumn>
      {
        <View>
          <Text>{ 'Overall: ' }</Text>
          <Text>{ overallStats }</Text>
        </View>
      }
      {
        <View>
          <Text>{ 'Last 12 months: ' }</Text>
          <Text>{ last12mStats === overallStats ? 'see above' : last12mStats || 'n/a' }</Text>
        </View>
      }
    </FlexColumn>
  );
};

const formatAssignmentStatus = assignmentStatus => assignmentStatus && assignmentStatus.toLowerCase();

const PotentialReviewer = ({
  potentialReviewer: {
    person = {},
    'author-of-manuscripts': authorOfManuscripts = [],
    'reviewer-of-manuscripts': reviewerOfManuscripts = [],
    'assignment-status': assignmentStatus,
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
      {
        assignmentStatus && (
          <Text style={ styles.assignmentStatus }>
            { ` (${formatAssignmentStatus(assignmentStatus['status'])})` }
          </Text>
        )
      }
      {
        person['email'] && (
          <PersonEmailLink person={ person } />
        )
      }
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
  const renderedStats = renderStats(person['stats']);
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
          renderedStats && (
            <View style={ styles.potentialReviewer.subSection }>
              <Text style={ styles.potentialReviewer.label }>Review Time: </Text>
              <View style={ styles.potentialReviewer.value }>
                { renderedStats }
              </View>
            </View>
          )
        }
        {
          (authorOfManuscripts.length > 0) && (
            <View
              style={ styles.potentialReviewer.subSection }
              className="potential-reviewer-author-of"
            >
              <Text style={ styles.potentialReviewer.label }>Author of: </Text>
              <View style={ styles.potentialReviewer.value }>
                <More lines={ 5 }>
                  <FlexColumn>
                    { renderManuscripts(authorOfManuscripts) }
                  </FlexColumn>
                </More>
              </View>
            </View>
          )
        }
        {
          (reviewerOfManuscripts.length > 0) && (
            <View
              style={ styles.potentialReviewer.subSection }
              className="potential-reviewer-reviewer-of"
            >
              <Text style={ styles.potentialReviewer.label }>Reviewer of: </Text>
              <View style={ styles.potentialReviewer.value }>
                <More lines={ 5 }>
                  <FlexColumn>
                    { renderManuscripts(reviewerOfManuscripts) }
                  </FlexColumn>
                </More>
              </View>
            </View>
          )
        }
        {
          (scores && scores['combined'] && (
            <View  style={ styles.potentialReviewer.subSection }>
              <Text style={ styles.potentialReviewer.label }>Scores: </Text>
              <View style={ styles.potentialReviewer.value }>
                <FlexColumn>
                      <InlineContainer>
                        <Score score={ scores }/>
                        <Text>{ ' (max across manuscripts)' }</Text>
                      </InlineContainer>
                </FlexColumn>
              </View>
            </View>
          )) || null
        }
      </CardText>
    </Card>
  );
};


const ManuscriptSummary = ({
  manuscript: {
    title,
    'manuscript-no': manuscriptNo,
    abstract,
    authors,
    reviewers,
    editors,
    'senior-editors': seniorEditors,
    'subject-areas': subjectAreas
  }
}) => (
  <Card style={ styles.manuscriptSummary.container } initiallyExpanded={ true }>
    <CardHeader
      title={ quote(title) }
      subtitle={ manuscriptNo }
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
      {
        reviewers && reviewers.length > 0 && (
          <View  style={ styles.manuscriptSummary.subSection }>
            <Text style={ styles.manuscriptSummary.label }>Reviewers: </Text>
            {
              reviewers.map((reviewer, index) => (
                <PersonInlineSummary key={ index } person={ reviewer }/>
              ))
            }
          </View>
        )
      }
      {
        editors && editors.length > 0 && (
          <View  style={ styles.manuscriptSummary.subSection }>
            <Text style={ styles.manuscriptSummary.label }>Editors: </Text>
            {
              editors.map((editor, index) => (
                <PersonInlineSummary key={ index } person={ editor }/>
              ))
            }
          </View>
        )
      }
      {
        seniorEditors && seniorEditors.length > 0 && (
          <View  style={ styles.manuscriptSummary.subSection }>
            <Text style={ styles.manuscriptSummary.label }>Senior Editors: </Text>
            {
              seniorEditors.map((seniorEditor, index) => (
                <PersonInlineSummary key={ index } person={ seniorEditor }/>
              ))
            }
          </View>
        )
      }
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


const extractAllSubjectAreas = manuscripts => {
  const subjectAreas = new Set();
  if (manuscripts) {
    manuscripts.forEach(m => {
      (m['subject-areas'] || []).forEach(subjectArea => {
        subjectAreas.add(subjectArea);
      })
    });
  };
  return subjectAreas;
}

const filterReviewsByEarlyCareerResearcherStatus = (potentialReviewers, earlyCareerReviewer) =>
  potentialReviewers.filter(potentialReviewer =>
    potentialReviewer.person['is-early-career-researcher'] === earlyCareerReviewer
  );

const reviewerPersonId = reviewer => reviewer && reviewer.person && reviewer.person['person-id'];

const SearchResult = ({ searchResult, selectedReviewer, onClearSelection }) => {
  const {
    potentialReviewers = [],
    matchingManuscripts = [],
    manuscriptsNotFound,
    error
  } = searchResult;
  const requestedSubjectAreas = extractAllSubjectAreas(matchingManuscripts);
  const hasManuscriptsNotFound = manuscriptsNotFound && manuscriptsNotFound.length > 0;
  const filteredPotentialReviewers = !selectedReviewer ? potentialReviewers :
    potentialReviewers.filter(r => reviewerPersonId(r) === reviewerPersonId(selectedReviewer));
  return (
    <View className="result-list">
      {
        error && (
          <View style={ styles.errorMessage }>
            <Text>
              This is very unfortunate, but there seems to be some sort of technical issue.
              Have you tried turning it off and on again?
            </Text>
          </View>
        )
      }
      {
        hasManuscriptsNotFound && (
          <View style={ styles.errorMessage }>
            <Text>{ `Manuscript not found: ${manuscriptsNotFound.join(', ')}` }</Text>
          </View>
        )
      }
      {
        !selectedReviewer && matchingManuscripts.map((matchingManuscript, index) => (
          <ManuscriptSummary
            key={ index }
            manuscript={ matchingManuscript }
          />
        ))
      }
      {
        filteredPotentialReviewers.map((potentialReviewer, index) => (
          <PotentialReviewer
            key={ index }
            potentialReviewer={ potentialReviewer }
            requestedSubjectAreas={ requestedSubjectAreas }
          />
        ))
      }
      {
        !hasManuscriptsNotFound && !error && potentialReviewers.length === 0 && (
          <View style={ styles.errorMessage }>
            <Text>{ 'No potential reviewers found' }</Text>
          </View>
        )
      }
      {
        selectedReviewer && (
          <View style={ styles.buttons }>
            <RaisedButton
              primary={ true }
              onClick={ onClearSelection }
              label="Clear Selection"
            />
          </View>
        )
      }
    </View>
  );
};

export default SearchResult;
