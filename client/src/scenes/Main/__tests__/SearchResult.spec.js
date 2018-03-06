import React from 'react';

import test from 'tape';
import { shallow } from 'enzyme';

import '../../../polyfills/react';

import SearchResult from '../SearchResult';

const SEARCH_RESULT = {};

const MANUSCRIPT_1 = {
  manuscript_id: '12345'
};

const MANUSCRIPT_2 = {
  manuscript_id: '12345'
};

const POTENTIAL_REVIEWER_1 = {
  person: {person_id: '12345'}
};

const POTENTIAL_REVIEWER_2 = {
  person: {person_id: '12345'}
};

test('SearchResult', g => {
  g.test('.should be defined', t => {
    t.true(SearchResult);
    t.end();
  });

  g.test('.should render empty results', t => {
    const component = shallow(<SearchResult searchResult={ SEARCH_RESULT } />);
    t.true(component);
    t.end();
  });

  g.test('.should pass matching manuscript to ManuscriptSummary', t => {
    const searchResult = {
      ...SEARCH_RESULT,
      matchingManuscripts: [MANUSCRIPT_1]
    }
    const component = shallow(<SearchResult searchResult={ searchResult } />);
    const manuscriptSummaryComponent = component.find('ManuscriptSummary');
    t.equal(manuscriptSummaryComponent.props()['manuscript'], MANUSCRIPT_1);
    t.end();
  });

  g.test('.should pass selected manuscript to ManuscriptSummary', t => {
    const searchResult = {
      ...SEARCH_RESULT,
      matchingManuscripts: [MANUSCRIPT_1]
    }
    const component = shallow(<SearchResult
      searchResult={ searchResult } selectedManuscript={ MANUSCRIPT_2 }
    />);
    const manuscriptSummaryComponent = component.find('ManuscriptSummary');
    t.equal(manuscriptSummaryComponent.props()['manuscript'], MANUSCRIPT_2);
    t.end();
  });

  g.test('.should pass potential reviewers to PotentialReviewer', t => {
    const searchResult = {
      ...SEARCH_RESULT,
      potentialReviewers: [POTENTIAL_REVIEWER_1, POTENTIAL_REVIEWER_2]
    }
    const component = shallow(<SearchResult searchResult={ searchResult } />);
    const potentialReviewerComponent = component.find('PotentialReviewer');
    t.equal(potentialReviewerComponent.length, 2);
    t.equal(potentialReviewerComponent.at(0).props()['potentialReviewer'], POTENTIAL_REVIEWER_1);
    t.equal(potentialReviewerComponent.at(1).props()['potentialReviewer'], POTENTIAL_REVIEWER_2);
    t.end();
  });
});
