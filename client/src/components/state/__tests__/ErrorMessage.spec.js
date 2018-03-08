import React from 'react';

import test from 'tape';
import { render } from 'enzyme';

import { ErrorMessage, getErrorMessage, UNKNOWN_ERROR, ERROR_CODE_PREFIX } from '../ErrorMessage';

const ERROR = 'panic!';

test('ErrorMessage', g => {
  g.test('.should be defined', t => {
    t.true(ErrorMessage);
    t.end();
  });

  g.test('.should render unknown error message if error is blank', t => {
    const component = render(<ErrorMessage error={ '' } />);
    t.equal(component.text(), UNKNOWN_ERROR);
    t.end();
  });

  g.test('.should render simple error message', t => {
    const component = render(<ErrorMessage error={ ERROR } />);
    t.equal(component.text(), ERROR);
    t.end();
  });

  g.test('.should render simple error object with error property', t => {
    const error = {
      error: ERROR
    };
    const component = render(<ErrorMessage error={ error } />);
    t.equal(component.text(), getErrorMessage(error));
    t.end();
  });
});

test('AppError.getErrorMessage', g => {
  g.test('.should return simple error message', t => {
    t.equal(getErrorMessage(ERROR), ERROR);
    t.end();
  });

  g.test('.should return error property of error object', t => {
    t.equal(getErrorMessage({
      error: ERROR
    }), ERROR);
    t.end();
  });

  g.test('.should return errorMessage property of error object', t => {
    t.equal(getErrorMessage({
      errorMessage: ERROR
    }), ERROR);
    t.end();
  });

  g.test('.should convert number', t => {
    t.equal(getErrorMessage(123), ERROR_CODE_PREFIX + '123');
    t.end();
  });

  g.test('.should return unknown error if error is blank', t => {
    t.equal(getErrorMessage(''), UNKNOWN_ERROR);
    t.end();
  });

  g.test('.should return unknown error if error is undefined', t => {
    t.equal(getErrorMessage(undefined), UNKNOWN_ERROR);
    t.end();
  });

  g.test('.should return unknown error if error property is blank', t => {
    t.equal(getErrorMessage({
      error: ''
    }), UNKNOWN_ERROR);
    t.end();
  });
});
