import React from 'react';

import test from 'tape';
import { shallow } from 'enzyme';

import withAppLoadingIndicator from '../withAppLoadingIndicator';

const WrappedComponent = props => <div/>;

const Component = withAppLoadingIndicator(
  WrappedComponent,
  props => props.loading,
  props => props.error
);

const ERROR = 'panic!';

test('withAppLoadingIndicator', g => {
  g.test('.should be defined', t => {
    t.true(withAppLoadingIndicator);
    t.end();
  });

  g.test('.should render AppLoading', t => {
    const component = shallow(<Component loading={ true } />);
    t.equal(component.find('AppLoading').length, 1);
    t.end();
  });

  g.test('.should render AppError', t => {
    const component = shallow(<Component loading={ false } error={ ERROR } />);
    t.equal(component.find('AppError').props()['error'], ERROR);
    t.end();
  });

  g.test('.should render wrapped component', t => {
    const component = shallow(<Component loading={ false } error={ false } />);
    t.equal(component.find('WrappedComponent').length, 1);
    t.end();
  });
});
