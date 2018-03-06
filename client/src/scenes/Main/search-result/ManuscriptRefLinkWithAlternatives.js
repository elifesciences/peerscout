import React from 'react';

import {
  InlineContainer,
  Text
} from '../../../components';

import ManuscriptRefLink from './ManuscriptRefLink';

export const ManuscriptRefLinkWithAlternatives = ({ manuscript }) => (
  <InlineContainer>
    <ManuscriptRefLink manuscript={ manuscript }/>
    {
      manuscript.alternatives && manuscript.alternatives.map((alternative, i) =>
        (
          <InlineContainer key={ `alternative${i}` }>
            <Text>{ ', ' }</Text>
            <ManuscriptRefLink manuscript={ alternative }/>
          </InlineContainer>
        )
      )
    }
  </InlineContainer>
);

export default ManuscriptRefLinkWithAlternatives;
