import React from 'react';

import test from 'tape';
import { shallow, render } from 'enzyme';

import PotentialReviewer from '../PotentialReviewer';
import {
  formatAssignmentStatus,
  PersonAssignmentStatus,
  DatesNotAvailable,
} from '../PotentialReviewer';

import {
  formatPeriodNotAvailable
} from '../../formatUtils';

const MANUSCRIPT_1 = {manuscript_id: '12345'};

const MANUSCRIPT_2 = {manuscript_id: '22222'};

const MEMBERSHIP_1 = {member_type: 'ORCID', member_id: '12345'};

const POTENTIAL_REVIEWER_1 = {
  person: {person_id: '12345'}
};

const PERIOD_1 = {start_date: '2017-01-01', end_date: '2017-01-02'};

const ASSIGNMENT_STATUS_1 = {'status': 'test'};

test('PotentialReviewer', g => {
  g.test('.should be defined', t => {
    t.true(PotentialReviewer);
    t.end();
  });

  g.test('.should render author of manuscripts', t => {
    const potentialReviewer = {
      ...POTENTIAL_REVIEWER_1,
      author_of_manuscripts: [MANUSCRIPT_1, MANUSCRIPT_2]
    };
    const component = shallow(<PotentialReviewer potentialReviewer={ potentialReviewer } />);
    const manuscriptComponent = component.find('ManuscriptInlineSummary');
    t.equal(manuscriptComponent.length, 2);
    t.equal(manuscriptComponent.at(0).props()['manuscript'], MANUSCRIPT_1);
    t.equal(manuscriptComponent.at(1).props()['manuscript'], MANUSCRIPT_2);
    t.end();
  });

  g.test('.should render person score', t => {
    const potentialReviewer = {
      ...POTENTIAL_REVIEWER_1,
      scores: {combined: 1.0}
    };
    const component = shallow(<PotentialReviewer potentialReviewer={ potentialReviewer } />);
    const scoreComponent = component.find('PersonScore');
    t.equal(scoreComponent.props()['score'], potentialReviewer.scores);
    t.end();
  });


  g.test('.should render dates not available', t => {
    const potentialReviewer = {
      ...POTENTIAL_REVIEWER_1,
      person: {
        ...POTENTIAL_REVIEWER_1.person,
        dates_not_available: [PERIOD_1]
      }
    };
    const component = shallow(<PotentialReviewer potentialReviewer={ potentialReviewer } />);
    const scoreComponent = component.find('DatesNotAvailable');
    t.equal(scoreComponent.props()['datesNotAvailable'], potentialReviewer.person.dates_not_available);
    t.end();
  });

  g.test('.should render memberships in card title area', t => {
    const potentialReviewer = {
      ...POTENTIAL_REVIEWER_1,
      person: {
        ...POTENTIAL_REVIEWER_1.person,
        memberships: [MEMBERSHIP_1]
      }
    };
    const component = shallow(<PotentialReviewer potentialReviewer={ potentialReviewer } />);
    const cardHeaderComponent = component.find('CardHeader');
    const titleComponent = shallow(cardHeaderComponent.props()['title']);
    const membershipComponent = titleComponent.find('Membership');
    t.equal(membershipComponent.length, 1);
    t.end();
  });

  g.test('.should render assignment status in card title area', t => {
    const potentialReviewer = {
      ...POTENTIAL_REVIEWER_1,
      assignment_status: {status: 'test'}
    };
    const component = shallow(<PotentialReviewer potentialReviewer={ potentialReviewer } />);
    const cardHeaderComponent = component.find('CardHeader');
    const titleComponent = shallow(cardHeaderComponent.props()['title']);
    const assignmentStatusComponent = titleComponent.find('PersonAssignmentStatus');
    t.equal(assignmentStatusComponent.props()['assignmentStatus'], potentialReviewer.assignment_status);
    t.end();
  });

  g.test('.should render person email link in sub title area', t => {
    const potentialReviewer = {
      ...POTENTIAL_REVIEWER_1,
      person: {
        ...POTENTIAL_REVIEWER_1.person,
        email: 'person@test.org'
      }
    };
    const component = shallow(<PotentialReviewer potentialReviewer={ potentialReviewer } />);
    const cardHeaderComponent = component.find('CardHeader');
    const titleComponent = shallow(cardHeaderComponent.props()['subtitle']);
    const personEmailLinkComponent = titleComponent.find('PersonEmailLink');
    t.equal(personEmailLinkComponent.props()['person'], potentialReviewer.person);
    t.end();
  });
});

test('PotentialReviewer.PersonAssignmentStatus', g => {
  g.test('.should be defined', t => {
    t.true(PersonAssignmentStatus);
    t.end();
  });

  g.test('.should render assignment status', t => {
    const component = render(<PersonAssignmentStatus assignmentStatus={ ASSIGNMENT_STATUS_1 } />);
    t.equal(component.text(), formatAssignmentStatus(ASSIGNMENT_STATUS_1['status']));
    t.end();
  });
});

test('PotentialReviewer.DatesNotAvailable', g => {
  g.test('.should be defined', t => {
    t.true(DatesNotAvailable);
    t.end();
  });

  g.test('.should render single date not available', t => {
    const datesNotAvailable = [PERIOD_1];
    const component = render(<DatesNotAvailable datesNotAvailable={ datesNotAvailable } />);
    t.equal(component.text(), formatPeriodNotAvailable(datesNotAvailable[0]));
    t.end();
  });
});
