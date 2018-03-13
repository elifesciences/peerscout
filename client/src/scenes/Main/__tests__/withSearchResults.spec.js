import React from 'react';

import test from 'tape';
import { shallow, mount } from 'enzyme';
import sinon from 'sinon';
import deferred from 'deferred';

import withSandbox from '../../../utils/__tests__/withSandbox';

import {
  withSearchResults,
  convertSearchOptionsToParams,
  convertResultsResponse
} from '../withSearchResults';
import * as monitoringModule from '../../../monitoring';
import { getAuhenticationHeaders } from '../../../api'

const WrappedComponent = props => <div/>;

const ERROR = 'panic!';

const SEARCH_OPTIONS = {
  manuscriptNumber: '12345'
};

const SEARCH_OPTIONS_2 = {
  manuscriptNumber: '22222'
};

const SEARCH_RESULT = {
  potential_reviewers: []
};

const SEARCH_ERROR = {
  error: ERROR
};

const AUTHENITCATION_STATE = {
  authenticated: true
};

const createMockApi = () => ({
  recommendReviewers: sinon.stub(),
  isNotAuthorizedError: sinon.stub()
});

const createMockAuth = () => ({
  revalidateToken: sinon.stub()
});

const createMockProps = () => ({
  pushSearchOptions: sinon.stub(),
  reviewerRecommendationApi: createMockApi(),
  auth: createMockAuth(),
  authenticationState: AUTHENITCATION_STATE
});

test('withSearchResults', g => {
  g.test('.should be defined', t => {
    t.true(withSearchResults);
    t.end();
  });

  g.test('.should load results and pass results to wrapped component', withSandbox(t => {
    const responseDeferred = deferred();
    const responsePromise = responseDeferred.promise;
    const props = createMockProps();
    props.reviewerRecommendationApi.recommendReviewers.returns(responsePromise);

    const Component = withSearchResults(WrappedComponent);
    const component = mount(<Component { ...props } searchOptions={ SEARCH_OPTIONS } />);

    responseDeferred.resolve(SEARCH_RESULT);
    component.update();

    t.true(props.reviewerRecommendationApi.recommendReviewers.calledWith(
      convertSearchOptionsToParams(SEARCH_OPTIONS),
      getAuhenticationHeaders(AUTHENITCATION_STATE)
    ));

    t.deepEqual(component.find('WrappedComponent').props()['searchResults'], {
      loading: false,
      value: convertResultsResponse(SEARCH_RESULT)
    });
    t.end();
  }));

  g.test('.should pass error to wrapped component and call reportError', withSandbox(t => {
    const responseDeferred = deferred();
    const responsePromise = responseDeferred.promise;
    const props = createMockProps();
    props.reviewerRecommendationApi.recommendReviewers.returns(responsePromise);
    t.sandbox.stub(monitoringModule, 'reportError');

    const Component = withSearchResults(WrappedComponent);
    const component = mount(<Component { ...props } searchOptions={ SEARCH_OPTIONS } />);
    props.reviewerRecommendationApi.isNotAuthorizedError.returns(false);
    responseDeferred.reject(SEARCH_ERROR);
    component.update();

    t.deepEqual(component.find('WrappedComponent').props()['searchResults'], {
      loading: false,
      error: {
        ...SEARCH_ERROR,
        notAuthorized: false
      }
    });
    t.true(monitoringModule.reportError.calledOnce);
    t.end();
  }));

  g.test('.should revalidateToken if not authorized', withSandbox(t => {
    const responseDeferred = deferred();
    const responsePromise = responseDeferred.promise;
    const props = createMockProps();
    props.reviewerRecommendationApi.recommendReviewers.returns(responsePromise);
    t.sandbox.stub(monitoringModule, 'reportError');

    const Component = withSearchResults(WrappedComponent);
    const component = mount(<Component { ...props } searchOptions={ SEARCH_OPTIONS } />);
    props.reviewerRecommendationApi.isNotAuthorizedError.returns(true);
    responseDeferred.reject(SEARCH_ERROR);
    component.update();

    t.true(props.auth.revalidateToken.calledOnce);
    t.end();
  }));

  g.test('.should call pushSearchOptions with search options after change', withSandbox(t => {
    const responseDeferred = deferred();
    const responsePromise = responseDeferred.promise;
    const props = createMockProps();
    props.reviewerRecommendationApi.recommendReviewers.returns(responsePromise);

    const Component = withSearchResults(WrappedComponent);
    const component = mount(<Component { ...props } searchOptions={ SEARCH_OPTIONS } />);

    responseDeferred.resolve(SEARCH_RESULT);
    component.update();

    t.true(props.pushSearchOptions.notCalled, 'pushSearchOptions should not be called yet');

    component.setProps({
      ...props,
      searchOptions: SEARCH_OPTIONS_2
    });

    t.true(props.pushSearchOptions.called, 'pushSearchOptions should be called');

    t.true(props.reviewerRecommendationApi.recommendReviewers.calledWith(
      convertSearchOptionsToParams(SEARCH_OPTIONS_2),
      getAuhenticationHeaders(AUTHENITCATION_STATE)
    ), 'recommendReviewers should be called with new search results');

    t.end();
  }));

  g.test('.should pass loading indicator while debouncing', withSandbox(t => {
    const responseDeferred = deferred();
    const responsePromise = responseDeferred.promise;
    const props = createMockProps();
    props.reviewerRecommendationApi.recommendReviewers.returns(responsePromise);

    const wrappedComponentConstructor = sinon.spy();
    class _WrappedComponent extends React.Component {
      constructor(props) {
        super(props);
        wrappedComponentConstructor();
      }

      render() {
        return <WrappedComponent { ...this.props } />;
      }
    }

    const Component = withSearchResults(_WrappedComponent, undefined, props => props.debouncing);
    const component = mount(<Component { ...props } searchOptions={ SEARCH_OPTIONS } />);

    responseDeferred.resolve(SEARCH_RESULT);
    component.update();

    t.deepEqual(component.find('WrappedComponent').props()['searchResults'], {
      loading: false,
      value: convertResultsResponse(SEARCH_RESULT)
    });

    props.reviewerRecommendationApi.recommendReviewers.reset();

    component.setProps({debouncing: true});
    component.update();
    t.deepEqual(component.find('WrappedComponent').props()['searchResults'], {
      loading: true
    });
    t.equal(wrappedComponentConstructor.callCount, 1, 'component should not be re-created');

    t.end();
  }));
});

test('withSearchResults.convertSearchOptionsToParams', g => {
  g.test('.should not add limit by default', t => {
    const searchOptions = {
      ...SEARCH_OPTIONS,
      limit: null
    };
    t.equal(
      convertSearchOptionsToParams(searchOptions).limit,
      undefined
    );
    t.end();
  });

  g.test('.should add limit if in options', t => {
    const searchOptions = {
      ...SEARCH_OPTIONS,
      limit: '123'
    };
    t.equal(
      convertSearchOptionsToParams(searchOptions).limit,
      '123'
    );
    t.end();
  });
});

test('withSearchResults.convertResultsResponse', g => {
  g.test('.should include relatedManuscriptByVersionId', t => {
    const searchResults = {
      ...SEARCH_RESULT,
      related_manuscript_by_version_id: {'12345': 'manuscript1'}
    };
    t.equal(
      convertResultsResponse(searchResults).relatedManuscriptByVersionId,
      searchResults.related_manuscript_by_version_id
    );
    t.end();
  });
});
