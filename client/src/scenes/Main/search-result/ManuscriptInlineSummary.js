import React from 'react';

import {
  InlineContainer,
  Text,
  TooltipWrapper,
  View
} from '../../../components';

import ManuscriptTooltipContent from '../ManuscriptTooltipContent';
import Score from './Score';

import ManuscriptRefLink from './ManuscriptRefLink';
import ManuscriptRefLinkWithAlternatives from './ManuscriptRefLinkWithAlternatives';

import {
  quote,
  formatDate
} from '../formatUtils';

const styles = {
  inlineContainer: {
    display: 'inline-block'
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
};

export const hasMatchingSubjectAreas = (manuscript, requestedSubjectAreas) =>
  requestedSubjectAreas.length === 0 || !!(manuscript['subject_areas'] || []).filter(
    subjectArea => requestedSubjectAreas.has(subjectArea)
  )[0];

export const PublishedDate = ({ value }) => (
  <Text>{ formatDate(value) }</Text>
);

export const ManuscriptInlineSummary = ({ manuscript, scores = {}, requestedSubjectAreas }) => {
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
      <PublishedDate value={ manuscript.published_timestamp } />
      <Text>{ ' (' }</Text>
      <ManuscriptRefLinkWithAlternatives manuscript={ manuscript }/>
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

export default ManuscriptInlineSummary;
