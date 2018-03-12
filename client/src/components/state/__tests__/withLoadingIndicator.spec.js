import React from 'react';

import test from 'tape';
import { shallow, render, mount } from 'enzyme';

import LoadingIndicator from '../LoadingIndicator';
import { withLoadingErrorIndicator } from '../withLoadingErrorIndicator';

const WrappedComponent = props => <div>wrapped</div>;

const Component = withLoadingErrorIndicator({
  isLoading: props => props.loading,
  getError: props => props.error
})(WrappedComponent);

const ERROR = 'keep calm!';

test('withLoadingErrorIndicator', g => {
  g.test('.should be defined', t => {
    t.true(withLoadingErrorIndicator);
    t.end();
  });

  g.test('.should render LoadingIndicator', t => {
    const component = mount(<Component loading={ true } />);
    t.equal(component.find('LoadingIndicator').length, 1);
    t.end();
  });

  g.test('.should render ErrorMessage', t => {
    const component = mount(<Component loading={ false } error={ ERROR } />);
    t.equal(component.find('ErrorMessage').props()['error'], ERROR);
    t.end();
  });

  g.test('.should render wrapped component', t => {
    const component = mount(<Component loading={ false } error={ false } />);
    t.equal(component.find('WrappedComponent').length, 1);
    t.end();
  });
});
