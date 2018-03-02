import React from 'react';

import {
  InlineContainer
} from '../../../components';

import Score from './Score';

export const PersonScore = ({ score, person }) => (
  <InlineContainer
    className={
      person.is_early_career_researcher ?
      'person-score early-career-researcher-score' :
      'person-score'
    }
  >
    <Score score={ score }/>
  </InlineContainer>
);

export default PersonScore;
