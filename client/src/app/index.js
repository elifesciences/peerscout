import ReactDOM from 'react-dom';
import React from 'react';
import injectTapEventPlugin from 'react-tap-event-plugin';

import Root from './Root';

import '../polyfills';

import 'font-awesome/css/font-awesome.css';
import 'react-more/styles.css';
import 'd3-tip/examples/example-styles.css';
import '../styles/web.css';

injectTapEventPlugin();

document.addEventListener('DOMContentLoaded', ()=> {
  const container = document.createElement('div');
  container.classList.add('app-container');
  document.body.appendChild(container);
  ReactDOM.render(
    React.createElement(Root),
    container
  );
});
