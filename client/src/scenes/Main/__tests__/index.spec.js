import React from 'react';

import test from 'tape';
import { shallow } from 'enzyme';
import sinon from 'sinon';

import '../../../polyfills/react';
import 'jsdom';

import Main, { MainView } from '../index';

const SEARCH_RESULTS = {
  potentialReviewers: [{
    person: {
      person_id: 'person1'
    }
  }]
};

const MANUSCRIPT_NOT_FOUND_SEARCH_RESULTS = {
  potentialReviewers: [],
  manuscriptsNotFound: ['manuscript1']
};

const SEARCH_ERROR = {
  error: 'bang',
  notAuthorized: true
};

const createMockLocalStorage = () => ({
  getItem: sinon.stub()
});

const createMockProps = () => ({
  config: {},
  searchResults: {},
  authenticationState: {},
  localStorage: createMockLocalStorage()
});

const resolved = value => ({loading: false, value});
const rejected = error => ({loading: false, error});

test('Main', g => {
  g.test('.should be defined', t => {
    t.true(Main);
    t.end();
  });
});

test('Main.MainView', g => {
  g.test('.should be defined', t => {
    t.true(MainView);
    t.end();
  });

  g.test('.should pass search results to SearchResult and ChartResult components', t => {
    const props = {
      ...createMockProps(),
      searchResults: resolved(SEARCH_RESULTS)
    };
    const component = shallow(<MainView { ...props } />);
    t.equals(component.find('SearchResult').props()['searchResult'], SEARCH_RESULTS);
    t.equals(component.find('ChartResult').props()['searchResult'], SEARCH_RESULTS);
    t.end();
  });

  g.test('.should pass not show ChartResult if there are no potential reviewers', t => {
    const props = {
      ...createMockProps(),
      searchResults: resolved(MANUSCRIPT_NOT_FOUND_SEARCH_RESULTS)
    };
    const component = shallow(<MainView { ...props } />);
    t.equals(component.find('ChartResult').length, 0);
    t.end();
  });

  g.test('.should pass manuscripts not found error to SearchResult component', t => {
    const props = {
      ...createMockProps(),
      searchResults: resolved(MANUSCRIPT_NOT_FOUND_SEARCH_RESULTS)
    };
    const component = shallow(<MainView { ...props } />);
    t.equals(
      component.find('SearchResult').props()['searchResult'], MANUSCRIPT_NOT_FOUND_SEARCH_RESULTS
    );
    t.end();
  });

  g.test('.should pass searchResults rejected error to SearchResult component', t => {
    const props = {
      ...createMockProps(),
      searchResults: rejected(SEARCH_ERROR)
    };
    const component = shallow(<MainView { ...props } />);
    t.equals(
      component.find('SearchResult').props()['error'], SEARCH_ERROR
    );
    t.end();
  });
});
