import test from 'tape';

import {
  recommendedReviewersToGraph
} from '../ChartResult';

test('ChartResult', g => {
  g.test('recommendedReviewersToGraph', g2 => {
    g2.test('should only include search node if no reviewers have been recommended', t => {
      const graph = recommendedReviewersToGraph([]);
      t.deepEqual(graph.nodes.map(n => n.id), ['search']);
      t.end();
    });
  });
});
