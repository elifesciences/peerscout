import React from 'react';

import AppThemeProvider from './AppThemeProvider';

import { Main } from '../scenes';

import config from '../config';
import { reviewerRecommendationApi } from '../api';

const apiUrl = config['API_URL'] || '/api';
console.log('apiUrl:', apiUrl);
const api = reviewerRecommendationApi(apiUrl);

const Root = props => (
  <AppThemeProvider>
    <Main reviewerRecommendationApi={ api }/>
  </AppThemeProvider>
);

export default Root;
