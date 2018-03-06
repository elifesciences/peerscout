import React from 'react';

import test from 'tape';

import '../../../polyfills/react';
import 'jsdom';

import Main from '../index';

test('Main', g => {
  g.test('.should be defined', t => {
    t.true(Main);
    t.end();
  });
});
