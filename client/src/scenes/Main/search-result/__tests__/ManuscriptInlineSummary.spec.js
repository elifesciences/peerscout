import React from 'react';

import test from 'tape';
import { shallow } from 'enzyme';

import ManuscriptInlineSummary from '../ManuscriptInlineSummary';

const MANUSCRIPT = {
  manuscript_id: '12345'
};

const SCORE = {
  keyword: 0.5,
  similarity: 0.5,
  combined: 1.0
};

test('ManuscriptInlineSummary', g => {
  g.test('.should be defined', t => {
    t.true(ManuscriptInlineSummary);
    t.end();
  });

  g.test('.should pass manuscript to ManuscriptRefLinkWithAlternatives', t => {
    const component = shallow(<ManuscriptInlineSummary
      manuscript={ MANUSCRIPT } requestedSubjectAreas={ [] }
    />);
    const linkComponent = component.find('ManuscriptRefLinkWithAlternatives');
    t.equal(linkComponent.props()['manuscript'], MANUSCRIPT);
    t.end();
  });

  g.test('.should pass score to Score', t => {
    const component = shallow(<ManuscriptInlineSummary
      manuscript={ MANUSCRIPT } requestedSubjectAreas={ [] } scores={ SCORE }
    />);
    const scoreComponent = component.find('Score');
    t.equal(scoreComponent.props()['score'], SCORE);
    t.end();
  });

  g.test('.should not add Score if no scores are provided', t => {
    const component = shallow(<ManuscriptInlineSummary
      manuscript={ MANUSCRIPT } requestedSubjectAreas={ [] }
    />);
    const scoreComponent = component.find('Score');
    t.equal(scoreComponent.length, 0);
    t.end();
  });
});
