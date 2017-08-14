import test from 'tape';

import {
  nodeReviewDurationEndAngle
} from '../node';

const PERSON_ID_1 = '2001';

const PERSON_1 = {
  person_id: PERSON_ID_1,
};

test('node', g => {
  g.test('.nodeReviewDurationEndAngle', g2 => {
    g2.test('..should return 0 if not potential reviewer', t => {
      t.equal(nodeReviewDurationEndAngle({}), 0);
      t.end();
    });

    g2.test('..should return 0 if potential reviewer has no stats', t => {
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

    g2.test('..should return greater than 0 if potential reviewer has overall stats', t => {
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
});
