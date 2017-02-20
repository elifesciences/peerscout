const urlWithParams = (url, params) => {
  const keys = Object.keys(params);
  return url + (keys.length === 0 ? '' :
    '?' + keys.map(key => `${key}=${encodeURIComponent(params[key])}`).join('&')
  )
};

const api = baseUrl => {
  const recommendReviewersUrl = baseUrl + '/recommend-reviewers';
  return {
    recommendReviewers: params => fetch(urlWithParams(recommendReviewersUrl, params), {
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
    // .then(text => { console.log('text:', text); return text; })
    .then(text => JSON.parse(text))
    // .then(response => response.json ? response.json() : response)
  };
};

export default api;
