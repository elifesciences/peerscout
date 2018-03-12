import React from 'react';

import test from 'tape';
import { shallow, mount } from 'enzyme';
import sinon from 'sinon';

import { withPromisedProp, withPromisedPropEnhancer } from '../withPromisedProp';

import deferred from 'deferred';

const WrappedComponent = props => (<div></div>);

const DATA_PROP = 'data';
const RESOLVED_VALUE = 'resolved';
const RESOLVED_VALUE_2 = 'resolved2';
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
    const component = mount(<Component other="123" />);
    const wrappedComponent = component.find('WrappedComponent');
    t.equal(wrappedComponent.props()['other'], '123');
    t.end();
  });

  g.test('.should pass resolved value to wrapped component', t => {
    const d = deferred();
    const load = sinon.spy(() => d.promise);
    const Component = withPromisedProp(
      WrappedComponent, load, DATA_PROP
    );
    const component = mount(<Component />);
    t.deepEqual(component.find('WrappedComponent').props()[DATA_PROP], {loading: true});

    d.resolve(RESOLVED_VALUE);
    component.update();
    const wrappedComponent = component.find('WrappedComponent');
    t.deepEqual(wrappedComponent.props()[DATA_PROP], {loading: false, value: RESOLVED_VALUE});
    t.equal(load.callCount, 1, 'load should be called once');

    t.end();
  });

  g.test('.should pass error to wrapped component', t => {
    const d = deferred();
    const load = sinon.spy(() => d.promise);
    const Component = withPromisedProp(
      WrappedComponent, load, DATA_PROP
    );
    const component = mount(<Component />);
    t.deepEqual(component.find('WrappedComponent').props()[DATA_PROP], {loading: true});

    d.reject(ERROR);
    component.update();
    const wrappedComponent = component.find('WrappedComponent');
    t.deepEqual(wrappedComponent.props()[DATA_PROP], {loading: false, error: ERROR});
    t.equal(load.callCount, 1, 'load should be called once');

    t.end();
  });

  g.test('.should reload on property change', t => {
    let d = deferred();
    const load = sinon.spy(() => d.promise);
    const Component = withPromisedProp(
      WrappedComponent, load, DATA_PROP, props => props.trigger
    );
    const component = mount(<Component trigger={ 1 } />);
    d.resolve(RESOLVED_VALUE);
    component.update();
    t.deepEqual(component.find('WrappedComponent').props()[DATA_PROP], {loading: false, value: RESOLVED_VALUE});

    d = deferred();
    component.setProps({trigger: 2});
    component.update();
    t.deepEqual(component.find('WrappedComponent').props()[DATA_PROP], {loading: true});

    d.resolve(RESOLVED_VALUE_2);
    component.update();
    t.deepEqual(component.find('WrappedComponent').props()[DATA_PROP], {loading: false, value: RESOLVED_VALUE_2});

    t.equal(load.callCount, 2, 'load should be called twice');

    t.end();
  });
});

test('withPromisedProp.withPromisedPropEnhancer', g => {
  g.test('.should be defined', t => {
    t.true(withPromisedPropEnhancer);
    t.end();
  });

  g.test('.should pass custom prop to wrapped component', t => {
    const Component = withPromisedPropEnhancer(
      () => Promise.resolve(null), DATA_PROP
    )(WrappedComponent);
    const component = mount(<Component other="123" />);
    const wrappedComponent = component.find('WrappedComponent');
    t.equal(wrappedComponent.props()['other'], '123');
    t.end();
  });
});
