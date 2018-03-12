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

import {
  duplicateManuscriptTitlesAsAlternatives,
  sortManuscriptsByPublishedTimestampDescending
} from '../manuscriptUtils';

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
      width: LABEL_WIDTH,
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

export const RelatedManuscripts = ({label, manuscripts, requestedSubjectAreas}) => (
  <View
    style={ styles.potentialReviewer.subSection }
  >
    <Text style={ styles.potentialReviewer.label }>{ `${label}  of:` }</Text>
    <View style={ styles.potentialReviewer.value }>
      <More lines={ 5 }>
        <FlexColumn>
          {
            manuscripts.map((manuscript, index) => (
              <ManuscriptInlineSummary
                key={ index }
                manuscript={ manuscript }
                requestedSubjectAreas={ requestedSubjectAreas }
              />
            ))
          }
        </FlexColumn>
      </More>
    </View>
  </View>
);

const PotentialReviewer = ({
  potentialReviewer,
  relatedManuscriptByVersionId,
  requestedSubjectAreas,
  onSelectPotentialReviewer  
}) => {
  const {
    person = {},
    related_manuscript_version_ids_by_relationship_type = [],
    assignment_status: assignmentStatus,
    scores = {}
  } = potentialReviewer;
  const onSelectThisPotentialReviewer = () => {
    if (onSelectPotentialReviewer) {
      onSelectPotentialReviewer(potentialReviewer);
    }
  };
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
  const getRelatedManuscriptByVersionIds = versionIds => (
    versionIds && versionIds.map(versionId => relatedManuscriptByVersionId[versionId])
  );
  const getRelatedManuscripts = relationshipType => duplicateManuscriptTitlesAsAlternatives(
    sortManuscriptsByPublishedTimestampDescending(
      relatedManuscriptByVersionId && related_manuscript_version_ids_by_relationship_type &&
      getRelatedManuscriptByVersionIds(
        related_manuscript_version_ids_by_relationship_type[relationshipType]
      )
    )
  ) || [];
  const relatedManuscriptsInfoList = [
    {label: 'Author', manuscripts: getRelatedManuscripts('author')},
    {label: 'Reviewing Editor', manuscripts: getRelatedManuscripts('editor')},
    {label: 'Senior Editor', manuscripts: getRelatedManuscripts('senior_editor')}
  ].filter(relatedManuscriptsInfo => relatedManuscriptsInfo.manuscripts.length > 0);
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
          relatedManuscriptsInfoList.map(relatedManuscriptsInfoList => (
            <RelatedManuscripts
              key={ relatedManuscriptsInfoList.label }
              label={ relatedManuscriptsInfoList.label }
              manuscripts={ relatedManuscriptsInfoList.manuscripts }
              requestedSubjectAreas={ requestedSubjectAreas }
            />
          ))
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
