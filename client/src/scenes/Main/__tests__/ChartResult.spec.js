import test from 'tape';

import {
  recommendedReviewersToGraph
} from '../ChartResult';

const MANUSCRIPT_NODE_PREFIX = 'm';
const PERSON_NODE_PREFIX = 'p';
const SEARCH_NODE_ID = 'search';

const MANUSCRIPT_ID_1 = '1001';

const PERSON_ID_1 = '2001';

const MANUSCRIPT_1 = {
  manuscript_id: MANUSCRIPT_ID_1,
};

const PERSON_1 = {
  person_id: PERSON_ID_1,
};

test('ChartResult', g => {
  g.test('recommendedReviewersToGraph', g2 => {
    g2.test('should only include search node if no reviewers have been recommended', t => {
      const graph = recommendedReviewersToGraph({});
      t.deepEqual(graph.nodes.map(n => n.id), [SEARCH_NODE_ID]);
      t.deepEqual(graph.links, []);
      t.end();
    });

    g2.test('should only include main manuscript node without recommended reviewers', t => {
      const graph = recommendedReviewersToGraph({
        matchingManuscripts: [MANUSCRIPT_1]
      });
      t.deepEqual(graph.nodes.map(n => n.id), [MANUSCRIPT_NODE_PREFIX + MANUSCRIPT_ID_1]);
      t.deepEqual(graph.links, []);
      t.end();
    });

    g2.test('should include one reviewer node with no manuscripts', t => {
      const graph = recommendedReviewersToGraph({
        potentialReviewers: [{
          person: PERSON_1
        }]
      });
      t.deepEqual(
        graph.nodes.map(n => n.id),
        [SEARCH_NODE_ID, PERSON_NODE_PREFIX + PERSON_ID_1]);
      t.deepEqual(
        graph.links.map(l => [l.source, l.target]),
        [[SEARCH_NODE_ID, PERSON_NODE_PREFIX + PERSON_ID_1]]
      );
      t.end();
    });

    g2.test('should include one reviewer node with one related manuscript', t => {
      const graph = recommendedReviewersToGraph({
        potentialReviewers: [{
          person: PERSON_1,
          author_of_manuscripts: [{
            ...MANUSCRIPT_1,
            authors: [PERSON_1]
          }]
        }]
      }, {
        showAllRelatedManuscripts: true
      });
      t.deepEqual(
        graph.nodes.map(n => n.id),
        [
          SEARCH_NODE_ID,
          PERSON_NODE_PREFIX + PERSON_ID_1,
          MANUSCRIPT_NODE_PREFIX + MANUSCRIPT_ID_1
        ]
      );
      t.deepEqual(
        graph.links.map(l => [l.source, l.target]),
        [
          [SEARCH_NODE_ID, PERSON_NODE_PREFIX + PERSON_ID_1],
          [MANUSCRIPT_NODE_PREFIX + MANUSCRIPT_ID_1, PERSON_NODE_PREFIX + PERSON_ID_1]
        ]
      );
      t.end();
    });
  });
});
