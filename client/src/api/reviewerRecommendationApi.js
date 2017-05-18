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

const fetchJson = url => fetch(url, {
  credentials: "same-origin"
})
.then(response => {
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

const api = baseUrl => {
  const getConfigUrl = baseUrl + '/config';
  const getAllSubjectAreasUrl = baseUrl + '/subject-areas';
  const getAllKeywordsUrl = baseUrl + '/keywords';
  const recommendReviewersUrl = baseUrl + '/recommend-reviewers';
  return {
    getConfig: () => fetchJson(urlWithParams(getConfigUrl, {})),
    getAllSubjectAreas: () => fetchJson(urlWithParams(getAllSubjectAreasUrl, {})),
    getAllKeywords: () => fetchJson(urlWithParams(getAllKeywordsUrl, {})),
    recommendReviewers: params => fetchJson(urlWithParams(recommendReviewersUrl, params))
  };
};

export default api;
