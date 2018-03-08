import React from 'react';

import { withPromisedProp } from '../../components';

import withResolvedPromise from './withResolvedPromise';

const DEFAULT_CONFIG = {
  showAllRelatedManuscripts: true,
  maxRelatedManuscripts: 15
};

const translateConfig = (configResult, defaultConfig) => {
  return {
    showAllRelatedManuscripts:
      configResult.chart_show_all_manuscripts != undefined ?
      configResult.chart_show_all_manuscripts == 'true' :
      defaultConfig.showAllRelatedManuscripts,
    maxRelatedManuscripts:
      configResult.max_related_manuscripts != undefined ?
      configResult.max_related_manuscripts :
      defaultConfig.maxRelatedManuscripts,
    auth0_domain: configResult.auth0_domain,
    auth0_client_id: configResult.auth0_client_id
  }
}

export const withConfig = (WrapperComponent, defaultConfig = DEFAULT_CONFIG) => withPromisedProp(
  WrapperComponent,
  props => props.reviewerRecommendationApi.getConfig().then(
    configResult => translateConfig(configResult, defaultConfig)
  ),
  'config'
);

export const withLoadedConfig = WrappedComponent => withConfig(
  withResolvedPromise(WrappedComponent, 'config')
);

export default withConfig;
