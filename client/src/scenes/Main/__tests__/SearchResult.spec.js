import React from 'react';

import test from 'tape';
import { shallow } from 'enzyme';

import '../../../polyfills/react';

import SearchResult, {
  getManuscriptsNotFoundMessage,
  NOT_AUTHORIZED_ERROR_MESSAGE,
  DEFAULT_ERROR_MESSAGE,
  NO_POTENTIAL_REVIEWERS_ERROR_MESSAGE
} from '../SearchResult';

const SEARCH_RESULT = {};

const MANUSCRIPTS_NOT_FOUND_RESULT = {
  manuscriptsNotFound: ['manuscript1']
};

const NO_POTENTIAL_REVIEWERS_RESULT = {
  potentialReviewers: []
};

const ERROR = 'bang!';

const NOT_AUTHORIZED_ERROR = {
  error: ERROR,
  notAuthorized: true
};

const VERSION_ID_1 = '11111-1';
const VERSION_ID_2 = '22222-1';

const MANUSCRIPT_1 = {
  manuscript_id: '12345',
  version_id: VERSION_ID_1
};

const MANUSCRIPT_2 = {
  manuscript_id: '12345',
  version_id: VERSION_ID_2
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

  g.test('.should pass selected manuscript version id to LazyManuscriptSummary', t => {
    const searchResult = {
      ...SEARCH_RESULT,
      matchingManuscripts: [MANUSCRIPT_1]
    }
    const component = shallow(<SearchResult
      searchResult={ searchResult } selectedManuscript={ MANUSCRIPT_2 }
    />);
    const manuscriptSummaryComponent = component.find('LazyManuscriptSummary');
    t.equal(manuscriptSummaryComponent.props()['versionId'], VERSION_ID_2);
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

  g.test('.should pass relatedManuscriptByVersionId to PotentialReviewer', t => {
    const relatedManuscriptByVersionId = {[VERSION_ID_1]: MANUSCRIPT_1};
    const searchResult = {
      ...SEARCH_RESULT,
      potentialReviewers: [POTENTIAL_REVIEWER_1],
      relatedManuscriptByVersionId
    }
    const component = shallow(<SearchResult searchResult={ searchResult } />);
    const potentialReviewerComponent = component.find('PotentialReviewer');
    t.equal(potentialReviewerComponent.length, 1);
    t.equal(
      potentialReviewerComponent.props()['relatedManuscriptByVersionId'],
      relatedManuscriptByVersionId
    );
    t.end();
  });

  g.test('.should show error message if error property is populated', t => {
    const component = shallow(<SearchResult error={ ERROR } />);
    t.equal(component.find('ErrorMessage').props()['error'], DEFAULT_ERROR_MESSAGE);
    t.end();
  });

  g.test('.should show not authorized error message if error has notAuthorized flag', t => {
    const component = shallow(<SearchResult error={ NOT_AUTHORIZED_ERROR } />);
    t.equal(component.find('ErrorMessage').props()['error'], NOT_AUTHORIZED_ERROR_MESSAGE);
    t.end();
  });

  g.test('.should show manuscripts not found error message', t => {
    const component = shallow(<SearchResult searchResult={ MANUSCRIPTS_NOT_FOUND_RESULT } />);
    t.equal(component.find('ErrorMessage').props()['error'], getManuscriptsNotFoundMessage(
      MANUSCRIPTS_NOT_FOUND_RESULT.manuscriptsNotFound
    ));
    t.end();
  });

  g.test('.should show no potential reviewers found error message', t => {
    const component = shallow(<SearchResult searchResult={ NO_POTENTIAL_REVIEWERS_RESULT } />);
    t.equal(component.find('ErrorMessage').props()['error'], NO_POTENTIAL_REVIEWERS_ERROR_MESSAGE);
    t.end();
  });
});
