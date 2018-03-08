import sinon from 'sinon';

const withSandbox = f => t => {
  const sandbox = sinon.sandbox.create();
  try {
    f({
      ...t,
      sandbox,
      end: () => {
        sandbox.restore();
        t.end();
      }
    });
  } finally {
    sandbox.restore();
  }
};

export default withSandbox;
