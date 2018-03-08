import React from 'react';

import test from 'tape';
import { shallow, mount } from 'enzyme';

import withPromisedProp from '../withPromisedProp';

import deferred from 'deferred';

const WrappedComponent = props => (<div></div>);

const DATA_PROP = 'data';
const RESOLVED_VALUE = 'resolved';
const ERROR = 'panic!';

test('withPromisedProp', g => {
  g.test('.should be defined', t => {
    t.true(withPromisedProp);
    t.end();
  });

  g.test('.should pass custom prop to wrapped component', t => {
    const Component = withPromisedProp(
      WrappedComponent, () => Promise.resolve(null), DATA_PROP
    );
    const component = shallow(<Component other="123" />);
    const wrappedComponent = component.find('WrappedComponent');
    t.equal(wrappedComponent.props()['other'], '123');
    t.end();
  });

  g.test('.should pass resolved value to wrapped component', t => {
    const d = deferred();
    const Component = withPromisedProp(
      WrappedComponent, () => d.promise, DATA_PROP
    );
    const component = mount(<Component />);
    d.resolve(RESOLVED_VALUE);
    component.update();
    const wrappedComponent = component.find('WrappedComponent');
    t.deepEqual(wrappedComponent.props()[DATA_PROP], {loading: false, value: RESOLVED_VALUE});
    t.end();
  });

  g.test('.should pass error to wrapped component', t => {
    const d = deferred();
    const Component = withPromisedProp(
      WrappedComponent, () => d.promise, DATA_PROP
    );
    const component = mount(<Component />);
    d.reject(ERROR);
    component.update();
    const wrappedComponent = component.find('WrappedComponent');
    t.deepEqual(wrappedComponent.props()[DATA_PROP], {loading: false, error: ERROR});
    t.end();
  });
});
