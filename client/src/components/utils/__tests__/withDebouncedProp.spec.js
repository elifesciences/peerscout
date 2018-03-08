import React from 'react';

import test from 'tape';
import { shallow } from 'enzyme';
import sinon from 'sinon';

import withDebouncedProp from '../withDebouncedProp';

const WrappedComponent = props => (<div></div>);

const VALUE_1 = 'value 1';
const VALUE_2 = 'value 2';

const createDebouncedPropTester = (t, options) => {
  const debounceFunction = sinon.stub();
  const debounce = sinon.stub().returns(debounceFunction);
  const triggerDebounce = () => debounce.getCall(0).args[0]();
  const Component = withDebouncedProp(
    WrappedComponent, props => props.inputValue, debouncedValue => ({debouncedValue}),
    {debounce, ...options}
  );
  return {
    Component,
    debounce,
    debounceFunction,
    triggerDebounce
  }
};

test('withDebouncedProp', g => {
  g.test('.should be defined', t => {
    t.true(withDebouncedProp);
    t.end();
  });

  g.test('.should pass custom prop to wrapped component', t => {
    const tester = createDebouncedPropTester(t);
    const component = shallow(<tester.Component other="123" />);
    t.equal(component.find('WrappedComponent').props()['other'], '123');
    t.end();
  });

  g.test('.should pass initial value to wrapped component', t => {
    const tester = createDebouncedPropTester(t);
    const component = shallow(<tester.Component inputValue={ VALUE_1 } />);
    t.equal(component.find('WrappedComponent').props().debouncedValue, VALUE_1);
    t.end();
  });

  g.test('.should debounce value change to wrapped component', t => {
    const tester = createDebouncedPropTester(t);
    const component = shallow(<tester.Component inputValue={ VALUE_1 } />);
    t.equal(component.find('WrappedComponent').props().debouncedValue, VALUE_1);

    component.setProps({inputValue: VALUE_2});
    component.update();
    t.equal(component.find('WrappedComponent').props().debouncedValue, VALUE_1);

    console.log('triggerDebounce');
    tester.triggerDebounce();
    component.update();
    t.equal(component.find('WrappedComponent').props().debouncedValue, VALUE_2);

    t.end();
  });

  g.test('.should optionally pass debouncing flag while debouncing', t => {
    const tester = createDebouncedPropTester(t, {
      debouncingProps: props => ({debouncing: true})
    });
    const component = shallow(<tester.Component inputValue={ VALUE_1 } />);
    t.equal(component.find('WrappedComponent').props().debouncedValue, VALUE_1);
    t.false(component.find('WrappedComponent').props().debouncing, 'should not be debouncing');

    component.setProps({inputValue: VALUE_2});
    component.update();
    t.equal(component.find('WrappedComponent').props().debouncedValue, VALUE_1);
    t.true(component.find('WrappedComponent').props().debouncing, 'should be debouncing');

    tester.triggerDebounce();
    component.update();
    t.equal(component.find('WrappedComponent').props().debouncedValue, VALUE_2);
    t.false(component.find('WrappedComponent').props().debouncing, 'should not be debouncing');

    t.end();
  });
});
