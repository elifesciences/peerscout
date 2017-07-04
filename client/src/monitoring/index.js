import TraceError from 'trace-error';

export const reportError = (message, error) => {
  console.log(message, error.message, error.stack);
  const newrelic = (self || window).newrelic;
  if (newrelic) {
    try {
      throw new TraceError(message, error);
    } catch (e) {
      newrelic.noticeError(e);
    }
  }
};
