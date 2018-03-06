import React from 'react';
import More from 'react-more';

import {
  Card,
  CardHeader,
  CardText,
  Comment,
  FlexColumn,
  InlineContainer,
  Text,
  View
} from '../../../components';

import { groupBy } from '../../../utils';

import ManuscriptInlineSummary from './ManuscriptInlineSummary';
import Membership from './Membership';
import PersonScore from './PersonScore';
import PersonWebSearchLink from './PersonWebSearchLink';
import PersonEmailLink from './PersonEmailLink';

import {
  formatCount,
  longPersonNameWithStatus,
  formatPeriodNotAvailable
} from '../formatUtils';

import { commonStyles } from '../../../styles';

const LABEL_WIDTH = 105;

const styles = {
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
      minWidth: LABEL_WIDTH,
      fontWeight: 'bold'
    },
    value: {
      flex: 1
    }
  },
  inlineContainer: {
    display: 'inline-block'
  },
};

export const formatAssignmentStatus = assignmentStatus => assignmentStatus && assignmentStatus.toLowerCase();

const formatDays = days =>
(days !== undefined) && `${days.toFixed(1)} ${days === 1.0 ? 'day' : 'days'}`;

const formatPeriodStats = periodStats => {
    const {
      mean,
      count
    } = periodStats['review_duration'] || {};
    return [
      mean && `${formatDays(mean)} (avg over ${formatCount(count, 'review', 'reviews')})`,
      formatCount(periodStats['reviews_in_progress'], 'review', 'reviews', 'in progress'),
      formatCount(periodStats['waiting_to_be_accepted'], 'review', 'reviews', 'awaiting response'),
      formatCount(periodStats['declined'], 'review', 'reviews', 'declined')
    ].filter(s => !!s).join(', ');
  }
  
const renderStats = stats => {
  const overallStats = formatPeriodStats((stats || {})['overall'] || {});
  const last12mStats = formatPeriodStats((stats || {})['last_12m'] || {});
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

export const PersonAssignmentStatus = ({ assignmentStatus }) => (
  <Text>{ formatAssignmentStatus(assignmentStatus['status']) }</Text>
);

export const DatesNotAvailable = ({ datesNotAvailable, style = {} }) => (
  <Text style={ style }>{ datesNotAvailable.map(formatPeriodNotAvailable).join(', ') }</Text>
);

const PotentialReviewer = ({
  potentialReviewer,
  requestedSubjectAreas,
  onSelectPotentialReviewer  
}) => {
  const {
    person = {},
    author_of_manuscripts: authorOfManuscripts = [],
    reviewer_of_manuscripts: reviewerOfManuscripts = [],
    assignment_status: assignmentStatus,
    scores = {}
  } = potentialReviewer;
  const onSelectThisPotentialReviewer = () => {
    if (onSelectPotentialReviewer) {
      onSelectPotentialReviewer(potentialReviewer);
    }
  };
  const manuscriptScoresByManuscriptNo = groupBy(scores['by_manuscript'] || [], s => s['manuscript_id']);
  const memberships = person.memberships || [];
  const membershipComponents = memberships.map((membership, index) => (
    <Membership key={ index } membership={ membership }/>
  ));
  if (membershipComponents.length === 0) {
    membershipComponents.push((<PersonWebSearchLink key="search" person={ person }/>));
  }
  const titleComponent = (
    <View style={ styles.inlineContainer }>
      <Text onClick={ onSelectThisPotentialReviewer }>{ longPersonNameWithStatus(person) }</Text>
      {
        assignmentStatus && (
          <Text style={ styles.assignmentStatus }>
            { ' (' }
            <PersonAssignmentStatus assignmentStatus={ assignmentStatus } />
            { ')' }
          </Text>
        )
      }
      { membershipComponents }
    </View>
  );
  const subtitleComponent = (
    <View style={ styles.inlineContainer }>
      <Text>{ person['institution'] }</Text>
      {
        person['email'] && (
          <PersonEmailLink person={ person } />
        )
      }
    </View>
  );
  const renderManuscripts = manuscripts => manuscripts && manuscripts.map((manuscript, index) => (
    <ManuscriptInlineSummary
      key={ index }
      manuscript={ manuscript }
      scores={ manuscriptScoresByManuscriptNo[manuscript['manuscript_id']] }
      requestedSubjectAreas={ requestedSubjectAreas }
    />
  ));
  const renderedStats = renderStats(person['stats']);
  const scoresNote = scores && scores.combined ?
    ' (max across manuscripts)' :
    ' Not enough data to calculate a score';
  return (
    <Card style={ styles.potentialReviewer.card }>
      <Comment text={ `Person id: ${person['person_id']}` }/>
      <CardHeader
        title={ titleComponent }
        subtitle={ subtitleComponent }
      />
      <CardText>
        {
          person['dates_not_available'] && person['dates_not_available'].length > 0 && (
            <View style={ styles.potentialReviewer.subSection }>
              <Text style={ styles.potentialReviewer.label }>Not Available: </Text>
              <DatesNotAvailable
                style={ styles.potentialReviewer.value }
                datesNotAvailable={ person['dates_not_available'] }
              />
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
              className="potential_reviewer_author_of"
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
              className="potential_reviewer_reviewer_of"
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
        <View  style={ styles.potentialReviewer.subSection }>
          <Text style={ styles.potentialReviewer.label }>Scores: </Text>
          <View style={ styles.potentialReviewer.value }>
            <FlexColumn>
              <InlineContainer onClick={ onSelectThisPotentialReviewer }>
                <PersonScore score={ scores } person={ person }/>
                <Text>{ scoresNote }</Text>
              </InlineContainer>
            </FlexColumn>
          </View>
        </View>
      </CardText>
    </Card>
  );
};

export default PotentialReviewer;
