import React from 'react';

import test from 'tape';
import { shallow } from 'enzyme';

import { NOT_AUTHORIZED_ERROR } from '../../../api';

import AppError, {
  UNKNOWN_ERROR,
  ERROR_CODE_PREFIX,
  getErrorMessage,
  AppErrorMessage
} from '../AppError';

const ERROR = 'panic!';
const AUTH = {auth: 'auth'};

test('AppError', g => {
  g.test('.should be defined', t => {
    t.true(AppError);
    t.end();
  });

  g.test('.should pass error to AppErrorMessage component', t => {
    const component = shallow(<AppError error={ ERROR } />);
    t.equal(component.find('AppErrorMessage').props()['error'], ERROR);
    t.end();
  });

  g.test('.should pass auth to LoggedInIndicator component', t => {
    const component = shallow(<AppError auth={ AUTH } />);
    t.equal(component.find('LoggedInIndicator').props()['auth'], AUTH);
    t.end();
  });
});

test('AppError.AppErrorMessage', g => {
  g.test('.should be defined', t => {
    t.true(AppErrorMessage);
    t.end();
  });

  g.test('.should pass error to ErrorMessage component', t => {
    const component = shallow(<AppErrorMessage error={ ERROR } />);
    t.equal(component.find('ErrorMessage').props()['error'], ERROR);
    t.end();
  });

  g.test('.should show not authorized message', t => {
    const component = shallow(<AppErrorMessage error={ NOT_AUTHORIZED_ERROR } />);
    t.equal(component.find('NotAuthorizedErrorMessage').length, 1);
    t.end();
  });
});
