import React from 'react';

import test from 'tape';
import { shallow, render } from 'enzyme';

import {
  formatCombinedScore,
  formatScoreWithDetails
} from '../../formatUtils';

import PersonScore from '../PersonScore';

const SCORE = {
  keyword: 0.5,
  similarity: 0.5,
  combined: 1.0
};

const PERSON = {person_id: 'person1'};

test('PersonScore', g => {
  g.test('.should be defined', t => {
    t.true(PersonScore);
    t.end();
  });

  g.test('.should pass score to Score component', t => {
    const component = shallow(<PersonScore score={ SCORE } person={ PERSON } />);
    const scoreComponent = component.find('Score');
    t.equal(scoreComponent.props()['score'], SCORE);
    t.end();
  });

  g.test('.should set className to "person-score" if not early career researcher', t => {
    const person = {...PERSON, is_early_career_researcher: false};
    const component = shallow(<PersonScore score={ SCORE } person={ person } />);
    t.equal(component.props()['className'], 'person-score');
    t.end();
  });

  g.test('.should set className to "person-score early-career-researcher-score" if early career researcher', t => {
    const person = {...PERSON, is_early_career_researcher: true};
    const component = shallow(<PersonScore score={ SCORE } person={ person } />);
    t.equal(component.props()['className'], 'person-score early-career-researcher-score');
    t.end();
  });
});
