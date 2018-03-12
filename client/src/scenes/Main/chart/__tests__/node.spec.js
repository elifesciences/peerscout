import test from 'tape';

import Set from 'es6-set';

import {
  nodeReviewDurationEndAngle,
  getNodeVersionIdFilter
} from '../node';

const VERSION_ID_1 = '1001-1';
const VERSION_ID_2 = '1002-1';

const PERSON_ID_1 = '2001';

const PERSON_1 = {
  person_id: PERSON_ID_1,
};

test('node.nodeReviewDurationEndAngle', g => {
  g.test('.should return 0 if not potential reviewer', t => {
    t.equal(nodeReviewDurationEndAngle({}), 0);
    t.end();
  });

  g.test('.should return 0 if potential reviewer has no stats', t => {
    t.equal(nodeReviewDurationEndAngle({
      potentialReviewer: {
        person: {
          ...PERSON_1,
          stats: {}
        }
      }
    }), 0);
    t.end();
  });

  g.test('.should return greater than 0 if potential reviewer has overall stats', t => {
    const value = nodeReviewDurationEndAngle({
      potentialReviewer: {
        person: {
          ...PERSON_1,
          stats: {
            overall: {
              review_duration: {
                mean: 1
              }
            }
          }
        }
      }
    });
    t.ok(value > 0, 'value should be greated than 0: ' + value);
    t.end();
  });
});
