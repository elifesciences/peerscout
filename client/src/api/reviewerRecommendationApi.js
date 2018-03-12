import TraceError from 'trace-error';

const urlWithParams = (url, params) => {
  const keys = Object.keys(params);
  return url + (keys.length === 0 ? '' :
    '?' + keys.map(key => `${key}=${encodeURIComponent(params[key])}`).join('&')
  )
};

const datetimeReviver = (key, value) =>
  key.endsWith('-date') && (typeof value === 'string') ?
  new Date(value) :
  value;

const logResponseTextEnabled = false;

const NOT_AUTHORIZED_STATUS = 401;
const NOT_AUTHORIZED_ERROR = 'NOT_AUTHORIZED_ERROR';

const fetchJson = (url, options) => fetch(url, {
  ...options,
  credentials: "same-origin"
})
.then(response => {
  if (response.status === NOT_AUTHORIZED_STATUS) {
    return Promise.reject(NOT_AUTHORIZED_ERROR);
  }
  if (response.status !== 200) {
    return Promise.reject('request failed');
  }
  console.log("response:", response);
  return response;
})
.then(response => response.text())
.then(text => text.replace(/NaN/g, null)) // TODO hack
.then(text => { logResponseTextEnabled && console.log('text:', text); return text; })
.then(text => JSON.parse(text, datetimeReviver))
.catch(err => {
  if (err === NOT_AUTHORIZED_ERROR) {
    return Promise.reject(err);
  }
  throw new TraceError('failed to fetch ' + url, err);
});

const api = baseUrl => {
  const getConfigUrl = baseUrl + '/config';
  const getAllSubjectAreasUrl = baseUrl + '/subject-areas';
  const getAllKeywordsUrl = baseUrl + '/keywords';
  const getSearchTypesUrl = baseUrl + '/search-types';
  const getManuscriptVersionUrl = versionId => `${baseUrl}/manuscript/version/${versionId}`;
  const recommendReviewersUrl = baseUrl + '/recommend-reviewers';
  return {
    getConfig: () => fetchJson(urlWithParams(getConfigUrl, {})),
    getAllSubjectAreas: () => fetchJson(urlWithParams(getAllSubjectAreasUrl, {})),
    getAllKeywords: () => fetchJson(urlWithParams(getAllKeywordsUrl, {})),
    getSearchTypes: options => fetchJson(urlWithParams(getSearchTypesUrl, {}), options),
    getManuscriptVersion: (versionId, options) => fetchJson(getManuscriptVersionUrl(versionId), options),
    recommendReviewers: (params, options) => fetchJson(urlWithParams(recommendReviewersUrl, params), options),
    isNotAuthorizedError: error => error === NOT_AUTHORIZED_ERROR
  };
};

export default api;
