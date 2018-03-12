import test from 'tape';

import { groupByMultiple } from '../arrayUtils';

const firstLetter = s => s[0];

test('arrayUtils.groupByMultiple', g => {
  g.test('.should return separate groups', t => {
    t.deepEqual(groupByMultiple(['a1', 'b1'], firstLetter), {
      'a': ['a1'],
      'b': ['b1']
    });
    t.end();
  });

  g.test('.should return items in same group', t => {
    t.deepEqual(groupByMultiple(['a1', 'a2'], firstLetter), {
      'a': ['a1', 'a2']
    });
    t.end();
  });

  g.test('.should allow undefined key', t => {
    t.deepEqual(groupByMultiple(['a1', 'a2'], () => undefined), {
      undefined: ['a1', 'a2']
    });
    t.end();
  });
});
