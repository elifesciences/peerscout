import React from 'react';

import {
  Text
} from '../../../components';

import {
  formatCombinedScore,
  formatScoreWithDetails
} from '../formatUtils';

export const NBSP = '\xa0';

export const Score = ({ score = {} }) => (
  <Text
    className="score"
    title={ (score.combined && formatScoreWithDetails(score)) || '' }
  >{ (score.combined && formatCombinedScore(score.combined)) || NBSP }</Text>
);

export default Score;
