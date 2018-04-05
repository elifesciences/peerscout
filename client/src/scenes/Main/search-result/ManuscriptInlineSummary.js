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
    display: 'inline-block'
  }
};

export const PublishedDate = ({ value }) => (
  <Text>{ formatDate(value) }</Text>
);

export const ManuscriptInlineSummary = ({ manuscript, scores = {} }) => {
  return (
    <View style={ styles.manuscriptInlineSummary }>
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
