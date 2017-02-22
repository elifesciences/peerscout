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
  Link,
  Text,
  TooltipWrapper,
  View
} from '../../components';

import { groupBy } from '../../utils';

import ManuscriptTooltipContent from './ManuscriptTooltipContent';

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
  }
}

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

const formatManuscriptId = manuscript => [
  manuscript['manuscript-no'],
  manuscript['version-no'] && `v${manuscript['version-no']}`
].filter(s => !!s).join(' ');

const formatKeywordScoreInline = keyword =>
  keyword ? keyword + ' keyword match' : '';

const formatSimilarityScoreInline = similarity =>
  similarity ? similarity.toFixed(2) + ' similarity' : '';

const doiUrl = doi => doi && 'http://dx.doi.org/' + doi;

const formatScoresInline = ({ keyword, similarity }) =>
  [
    formatKeywordScoreInline(keyword),
    formatSimilarityScoreInline(similarity)
  ].filter(s => !!s).join(', ');

const hasMatchingSubjectAreas = (manuscript, requestedSubjectAreas) =>
  requestedSubjectAreas.length === 0 || !!(manuscript['subject-areas'] || []).filter(
    subjectArea => requestedSubjectAreas.has(subjectArea)
  )[0];

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
  const formattedScores = formatScoresInline(scores);
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
      <Text>{ ' (' }</Text>
      <ManuscriptRefLink manuscript={ manuscript }/>
      <Text>{ ')' }</Text>
      {
        formattedScores && (
          <Text>{ ` - ${formattedScores}` }</Text>
        )
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
          person.stats && person.stats['review-duration'] && person.stats['review-duration']['mean'] && (
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
            <More lines={ 5 }>
              <FlexColumn>
                { renderManuscripts(authorOfManuscripts) }
              </FlexColumn>
            </More>
          </View>
        </View>
        <View  style={ styles.potentialReviewer.subSection }>
          <Text style={ styles.potentialReviewer.label }>Reviewer of: </Text>
          <View style={ styles.potentialReviewer.value }>
            <FlexColumn>
              <More lines={ 5 }>
                { renderManuscripts(reviewerOfManuscripts) }
              </More>
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

const filterReviewsByEarlyCareerReviewerStatus = (potentialReviewers, earlyCareerReviewer) =>
  potentialReviewers.filter(potentialReviewer =>
    potentialReviewer.person['is-early-career-reviewer'] === earlyCareerReviewer
  );

const shufflePotentialReviewers = potentialReviewers => {
  const nonEarlyCareerReviewers = filterReviewsByEarlyCareerReviewerStatus(
    potentialReviewers, false
  );
  const earlyCareerReviewers = filterReviewsByEarlyCareerReviewerStatus(
    potentialReviewers, true
  );
  const maxLength = Math.max(nonEarlyCareerReviewers.length, earlyCareerReviewers.length);
  const result = [];
  for (let i = 0; i < maxLength; i++) {
    if (nonEarlyCareerReviewers[i]) {
      result.push(nonEarlyCareerReviewers[i]);
    }
    if (earlyCareerReviewers[i]) {
      result.push(earlyCareerReviewers[i]);
    }
  }
  return result;
}

const SearchResult = ({ searchResult }) => {
  const { potentialReviewers = [], matchingManuscripts = [] } = searchResult;
  const requestedSubjectAreas = extractAllSubjectAreas(matchingManuscripts);
  const sortedPotentialReviewers = shufflePotentialReviewers(potentialReviewers);
  return (
    <View>
      {
        matchingManuscripts.map((matchingManuscript, index) => (
          <ManuscriptSummary
            key={ index }
            manuscript={ matchingManuscript }
          />
        ))
      }
      {
        sortedPotentialReviewers.map((potentialReviewer, index) => (
          <PotentialReviewer
            key={ index }
            potentialReviewer={ potentialReviewer }
            requestedSubjectAreas={ requestedSubjectAreas }
          />
        ))
      }
    </View>
  );
};

export default SearchResult;
