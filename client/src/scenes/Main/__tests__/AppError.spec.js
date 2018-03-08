import React from 'react';

import test from 'tape';
import { shallow } from 'enzyme';

import AppError, { UNKNOWN_ERROR, ERROR_CODE_PREFIX, getErrorMessage } from '../AppError';

const ERROR = 'panic!';

test('AppError', g => {
  g.test('.should be defined', t => {
    t.true(AppError);
    t.end();
  });

  g.test('.should pass error to ErrorMessage component', t => {
    const component = shallow(<AppError error={ ERROR } />);
    t.equal(component.find('ErrorMessage').props()['error'], ERROR);
    t.end();
  });
});
