import React from 'react';

import test from 'tape';
import { shallow, render } from 'enzyme';

import { formatDate } from '../../formatUtils';

import {
  ManuscriptInlineSummary,
  PublishedDate
} from '../ManuscriptInlineSummary';

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
      manuscript={ MANUSCRIPT }
    />);
    const linkComponent = component.find('ManuscriptRefLinkWithAlternatives');
    t.equal(linkComponent.props()['manuscript'], MANUSCRIPT);
    t.end();
  });

  g.test('.should pass manuscript published timestamp to PublishedDate', t => {
    const manuscript = {
      ...MANUSCRIPT,
      published_timestamp: '2017-01-01T00:00:00'
    };
    const component = shallow(<ManuscriptInlineSummary
      manuscript={ manuscript }
    />);
    t.equal(component.find('PublishedDate').props()['value'], manuscript.published_timestamp);
    t.end();
  });

  g.test('.should pass score to Score', t => {
    const component = shallow(<ManuscriptInlineSummary
      manuscript={ MANUSCRIPT } scores={ SCORE }
    />);
    const scoreComponent = component.find('Score');
    t.equal(scoreComponent.props()['score'], SCORE);
    t.end();
  });

  g.test('.should not add Score if no scores are provided', t => {
    const component = shallow(<ManuscriptInlineSummary
      manuscript={ MANUSCRIPT }
    />);
    const scoreComponent = component.find('Score');
    t.equal(scoreComponent.length, 0);
    t.end();
  });
});

test('ManuscriptInlineSummary.PublishedDate', g => {
  g.test('.should be defined', t => {
    t.true(PublishedDate);
    t.end();
  });

  g.test('.should pass manuscript to ManuscriptRefLinkWithAlternatives', t => {
    const timestamp = '2017-01-01T00:00:00';
    const component = render(<PublishedDate value={ timestamp } />);
    t.equal(component.text(), formatDate(timestamp));
    t.end();
  });
});
