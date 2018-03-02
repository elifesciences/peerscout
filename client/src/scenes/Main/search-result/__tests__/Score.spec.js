import React from 'react';

import test from 'tape';
import { shallow, render } from 'enzyme';

import {
  formatCombinedScore,
  formatScoreWithDetails
} from '../../formatUtils';

import Score from '../Score';
import { NBSP } from '../Score';

const SCORE = {
  keyword: 0.5,
  similarity: 0.5,
  combined: 1.0
};

const EMPTY_SCORE = {};

test('Score', g => {
  g.test('.should be defined', t => {
    t.true(Score);
    t.end();
  });

  g.test('.should render formatted combined score as text', t => {
    const component = render(<Score score={ SCORE } />);
    t.equal(component.text(), '' + formatCombinedScore(1.0));
    t.end();
  });

  g.test('.should render as non breaking space if no score is provided', t => {
    const component = render(<Score score={ EMPTY_SCORE } />);
    t.equal(component.text(), NBSP);
    t.end();
  })

  g.test('.should add score details title', t => {
    const component = shallow(<Score score={ SCORE } />);
    t.equal(component.props()['title'], formatScoreWithDetails(SCORE));
    t.end();
  });
});
