import React from 'react';

import test from 'tape';
import { shallow, render } from 'enzyme';

import ManuscriptSummary from '../ManuscriptSummary';
import {
  PersonInlineSummary,
  PersonListInlineSummary
} from '../ManuscriptSummary';

import {
  longPersonNameWithStatus
} from '../../formatUtils';

const PERSON_1 = {person_id: 'person1'};

const MANUSCRIPT = {
  manuscript_id: '12345',
  subject_areas: []
};

test('ManuscriptSummary', g => {
  g.test('.should be defined', t => {
    t.true(ManuscriptSummary);
    t.end();
  });

  g.test('.should render', t => {
    const component = shallow(<ManuscriptSummary manuscript={ MANUSCRIPT } />);
    t.true(component);
    t.end();
  });

  g.test('.should render authors', t => {
    const manuscript = {
      ...MANUSCRIPT,
      authors: [PERSON_1]
    };
    const component = shallow(<ManuscriptSummary manuscript={ manuscript } />);
    const personListComponent = component.find('PersonListInlineSummary');
    t.equal(personListComponent.props()['persons'], manuscript.authors);
    t.end();
  });
});

test('ManuscriptSummary.PersonInlineSummary', g => {
  g.test('.should be defined', t => {
    t.true(PersonInlineSummary);
    t.end();
  });

  g.test('.should render PersonInlineSummary', t => {
    const component = render(<PersonInlineSummary person={ PERSON_1 } />);
    t.equal(component.text(), longPersonNameWithStatus(PERSON_1));
    t.end();
  });
});

test('ManuscriptSummary.PersonListInlineSummary', g => {
  g.test('.should be defined', t => {
    t.true(PersonListInlineSummary);
    t.end();
  });

  g.test('.should render PersonInlineSummary', t => {
    const component = shallow(<PersonListInlineSummary persons={ [PERSON_1] } />);
    const personInlineSummaryComponent = component.find('PersonInlineSummary');
    t.equal(personInlineSummaryComponent.props()['person'], PERSON_1);
    t.end();
  });

  g.test('.should not add corresponding author indicator', t => {
    const person = {
      ...PERSON_1,
      is_corresponding_author: false
    };
    const component = shallow(<PersonListInlineSummary persons={ [person] } />);
    const correspondingAuthorIndicatorComponent = component.find('CorrespondingAuthorIndicator');
    t.equal(correspondingAuthorIndicatorComponent.length, 0);
    t.end();
  });

  g.test('.should add corresponding author indicator', t => {
    const person = {
      ...PERSON_1,
      is_corresponding_author: true
    };
    const component = shallow(<PersonListInlineSummary persons={ [person] } />);
    const correspondingAuthorIndicatorComponent = component.find('CorrespondingAuthorIndicator');
    t.equal(correspondingAuthorIndicatorComponent.props()['person'], person);
    t.end();
  });
});
