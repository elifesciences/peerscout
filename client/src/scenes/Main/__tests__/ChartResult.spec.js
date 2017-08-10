import test from 'tape';

import {
  recommendedReviewersToGraph,
  nodeReviewDurationEndAngle
} from '../ChartResult';

const MANUSCRIPT_NODE_PREFIX = 'm';
const PERSON_NODE_PREFIX = 'p';
const SEARCH_NODE_ID = 'search';

const MANUSCRIPT_ID_1 = '1001';
const MANUSCRIPT_ID_2 = '1002';
const MANUSCRIPT_ID_3 = '1003';

const VERSION_ID_1 = MANUSCRIPT_ID_1 + '-1';
const VERSION_ID_2 = MANUSCRIPT_ID_2 + '-1';
const VERSION_ID_3 = MANUSCRIPT_ID_3 + '-1';

const PERSON_ID_1 = '2001';

const MANUSCRIPT_1 = {
  manuscript_id: MANUSCRIPT_ID_1,
  version_id: VERSION_ID_1
};

const MANUSCRIPT_2 = {
  manuscript_id: MANUSCRIPT_ID_2,
  version_id: VERSION_ID_2
};

const MANUSCRIPT_3 = {
  manuscript_id: MANUSCRIPT_ID_3,
  version_id: VERSION_ID_3
};

const PERSON_1 = {
  person_id: PERSON_ID_1,
};

test('ChartResult', g => {
  g.test('.recommendedReviewersToGraph', g2 => {
    g2.test('..should only include search node if no reviewers have been recommended', t => {
      const graph = recommendedReviewersToGraph({});
      t.deepEqual(graph.nodes.map(n => n.id), [SEARCH_NODE_ID]);
      t.deepEqual(graph.links, []);
      t.end();
    });

    g2.test('..should only include main manuscript node without recommended reviewers', t => {
      const graph = recommendedReviewersToGraph({
        matchingManuscripts: [MANUSCRIPT_1]
      });
      t.deepEqual(graph.nodes.map(n => n.id), [MANUSCRIPT_NODE_PREFIX + MANUSCRIPT_ID_1]);
      t.deepEqual(graph.links, []);
      t.end();
    });

    g2.test('..should include one reviewer node with no manuscripts', t => {
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

    g2.test('..should include one reviewer node with one related manuscript', t => {
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

    g2.test('..should add multiple related manuscripts', t => {
      const graph = recommendedReviewersToGraph({
        potentialReviewers: [{
          person: PERSON_1,
          author_of_manuscripts: [{
            ...MANUSCRIPT_1,
            authors: [PERSON_1]
          }, {
            ...MANUSCRIPT_2,
            authors: [PERSON_1]
          }, {
            ...MANUSCRIPT_3,
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
          MANUSCRIPT_NODE_PREFIX + MANUSCRIPT_ID_1,
          MANUSCRIPT_NODE_PREFIX + MANUSCRIPT_ID_2,
          MANUSCRIPT_NODE_PREFIX + MANUSCRIPT_ID_3
        ]
      );
      t.deepEqual(
        graph.links.map(l => [l.source, l.target]),
        [
          [SEARCH_NODE_ID, PERSON_NODE_PREFIX + PERSON_ID_1],
          [MANUSCRIPT_NODE_PREFIX + MANUSCRIPT_ID_1, PERSON_NODE_PREFIX + PERSON_ID_1],
          [MANUSCRIPT_NODE_PREFIX + MANUSCRIPT_ID_2, PERSON_NODE_PREFIX + PERSON_ID_1],
          [MANUSCRIPT_NODE_PREFIX + MANUSCRIPT_ID_3, PERSON_NODE_PREFIX + PERSON_ID_1]
        ]
      );
      t.end();
    });

    g2.test('..should not add more than configured maximum related manuscripts', t => {
      const graph = recommendedReviewersToGraph({
        potentialReviewers: [{
          person: PERSON_1,
          author_of_manuscripts: [{
            ...MANUSCRIPT_1,
            authors: [PERSON_1]
          }, {
            ...MANUSCRIPT_2,
            authors: [PERSON_1]
          }, {
            ...MANUSCRIPT_3,
            authors: [PERSON_1]
          }]
        }]
      }, {
        showAllRelatedManuscripts: true,
        maxRelatedManuscripts: 2
      });
      t.deepEqual(
        graph.nodes.map(n => n.id),
        [
          SEARCH_NODE_ID,
          PERSON_NODE_PREFIX + PERSON_ID_1,
          MANUSCRIPT_NODE_PREFIX + MANUSCRIPT_ID_1,
          MANUSCRIPT_NODE_PREFIX + MANUSCRIPT_ID_2
        ]
      );
      t.deepEqual(
        graph.links.map(l => [l.source, l.target]),
        [
          [SEARCH_NODE_ID, PERSON_NODE_PREFIX + PERSON_ID_1],
          [MANUSCRIPT_NODE_PREFIX + MANUSCRIPT_ID_1, PERSON_NODE_PREFIX + PERSON_ID_1],
          [MANUSCRIPT_NODE_PREFIX + MANUSCRIPT_ID_2, PERSON_NODE_PREFIX + PERSON_ID_1]
        ]
      );
      t.end();
    });

    g2.test('..should sort related manuscripts and not add more than configured maximum', t => {
      const graph = recommendedReviewersToGraph({
        potentialReviewers: [{
          person: PERSON_1,
          author_of_manuscripts: [{
            ...MANUSCRIPT_1,
            authors: [PERSON_1]
          }, {
            ...MANUSCRIPT_2,
            authors: [PERSON_1]
          }, {
            ...MANUSCRIPT_3,
            authors: [PERSON_1]
          }],
          scores: {
            by_manuscript: [{
              version_id: VERSION_ID_1,
              combined: 0.9
            }, {
              version_id: VERSION_ID_2,
              combined: 0.7
            }, {
              version_id: VERSION_ID_3,
              combined: 0.8
            }]
          }
        }]
      }, {
        showAllRelatedManuscripts: true,
        maxRelatedManuscripts: 2
      });
      t.deepEqual(
        graph.nodes.map(n => n.id),
        [
          SEARCH_NODE_ID,
          PERSON_NODE_PREFIX + PERSON_ID_1,
          MANUSCRIPT_NODE_PREFIX + MANUSCRIPT_ID_1,
          MANUSCRIPT_NODE_PREFIX + MANUSCRIPT_ID_3
        ]
      );
      t.deepEqual(
        graph.links.map(l => [l.source, l.target]),
        [
          [SEARCH_NODE_ID, PERSON_NODE_PREFIX + PERSON_ID_1],
          [MANUSCRIPT_NODE_PREFIX + MANUSCRIPT_ID_1, PERSON_NODE_PREFIX + PERSON_ID_1],
          [MANUSCRIPT_NODE_PREFIX + MANUSCRIPT_ID_3, PERSON_NODE_PREFIX + PERSON_ID_1]
        ]
      );
      t.end();
    });
  });

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
