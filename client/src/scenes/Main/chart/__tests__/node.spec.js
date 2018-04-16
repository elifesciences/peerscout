import test from 'tape';

import Set from 'es6-set';

import * as d3 from 'd3';

import {
  recommendedReviewersToGraph,
  manuscriptIdToNodeId,
  personIdToNodeId
} from '../graph';

import {
  nodeReviewDurationEndAngle,
  getNodeVersionIdFilter,
  createNode,
  selectNodeByReviewer,
  selectNodeByNode,
  SELECTED_NODE_CLASS,
  CORRESPONDING_AUTHOR_CLASS,
  MANUSCRIPT_OF_CORRESPONDING_AUTHOR_CLASS
} from '../node';

import {
  PERSON_ID_1,
  PERSON_1,
  MANUSCRIPT_ID_1,
  VERSION_ID_1,
  VERSION_ID_2,
  MANUSCRIPT_1
} from './graph.spec';
import { tree } from 'd3-hierarchy';

const POTENTIAL_REVIEWER_1 = {
  person: PERSON_1
};

const DEFAULT_GRAPH_OPTIONS = {
  showAllRelatedManuscripts: true
};

const POTENTIAL_REVIEWER_AS_NON_CORRESPONDING_AUTHOR = {
  ...POTENTIAL_REVIEWER_1,
  related_manuscript_version_ids_by_relationship_type: {
    author: [VERSION_ID_1]
  }
};

const POTENTIAL_REVIEWER_AS_CORRESPONDING_AUTHOR = {
  ...POTENTIAL_REVIEWER_1,
  related_manuscript_version_ids_by_relationship_type: {
    author: [VERSION_ID_1],
    corresponding_author: [VERSION_ID_1]
  }
};

const SEARCH_RESULT_WITH_POTENTIAL_REVIEWER = {
  potentialReviewers: [POTENTIAL_REVIEWER_1]
};

const SEARCH_RESULT_WITH_NON_CORRESPONDING_AUTHOR = {
  potentialReviewers: [POTENTIAL_REVIEWER_AS_NON_CORRESPONDING_AUTHOR],
  relatedManuscriptByVersionId: {
    [VERSION_ID_1]: MANUSCRIPT_1
  }
};

const SEARCH_RESULT_WITH_CORRESPONDING_AUTHOR = {
  ...SEARCH_RESULT_WITH_NON_CORRESPONDING_AUTHOR,
  potentialReviewers: [POTENTIAL_REVIEWER_AS_CORRESPONDING_AUTHOR]
};


const createGraphTester = (searchResult, options = DEFAULT_GRAPH_OPTIONS) => {
  const view = d3.select(document.createElement('svg'));
  const graph = recommendedReviewersToGraph(searchResult, options);
  const node = createNode(view, graph.nodes);
  const nodesByClass = styleClass => view.selectAll(`.${styleClass}`);

  const nodeById = nodeId => {
    const matchingNode = graph.nodes.filter(n => n.id === nodeId)[0];
    if (!matchingNode) {
      const ids = graph.nodes.map(n => n.id);
      throw `node not found: ${nodeId}, available ids: ${ids}`;
    }
    return matchingNode;
  };

  const nodeByManuscriptId = manuscriptId => nodeById(manuscriptIdToNodeId(manuscriptId));
  const nodeByPersonId = personId => nodeById(personIdToNodeId(personId));

  return {
    view,
    graph,
    node,
    nodesByClass,
    nodeByManuscriptId,
    nodeByPersonId
  }
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

test('node.selectNodeByReviewer', g => {
  g.test('.should select reviewer node itself', t => {
    const { nodesByClass, graph, node } = createGraphTester(
      SEARCH_RESULT_WITH_POTENTIAL_REVIEWER
    );

    t.equal(nodesByClass(SELECTED_NODE_CLASS).size(), 0);
    selectNodeByReviewer(node, POTENTIAL_REVIEWER_1);
    t.equal(nodesByClass(SELECTED_NODE_CLASS).size(), 1);

    t.end();
  });

  g.test('.should not select nodes if reviewer is null', t => {
    const { nodesByClass, graph, node } = createGraphTester(
      SEARCH_RESULT_WITH_POTENTIAL_REVIEWER
    );

    selectNodeByReviewer(node, null);
    t.equal(nodesByClass(SELECTED_NODE_CLASS).size(), 0);

    t.end();
  });

  g.test('.should not select manuscripts reviewer is not corresponding author of', t => {
    const { nodesByClass, graph, node } = createGraphTester(
      SEARCH_RESULT_WITH_NON_CORRESPONDING_AUTHOR
    );

    t.equal(nodesByClass(MANUSCRIPT_OF_CORRESPONDING_AUTHOR_CLASS).size(), 0);
    selectNodeByReviewer(node, POTENTIAL_REVIEWER_AS_NON_CORRESPONDING_AUTHOR);
    t.equal(nodesByClass(MANUSCRIPT_OF_CORRESPONDING_AUTHOR_CLASS).size(), 0);

    t.end();
  });

  g.test('.should select manuscripts reviewer is corresponding author of', t => {
    const { nodesByClass, graph, node } = createGraphTester(
      SEARCH_RESULT_WITH_CORRESPONDING_AUTHOR
    );

    t.equal(nodesByClass(MANUSCRIPT_OF_CORRESPONDING_AUTHOR_CLASS).size(), 0);
    selectNodeByReviewer(node, POTENTIAL_REVIEWER_AS_CORRESPONDING_AUTHOR);
    t.equal(nodesByClass(MANUSCRIPT_OF_CORRESPONDING_AUTHOR_CLASS).size(), 1);

    t.end();
  });
});

test('node.selectNodeByNode', g => {
  g.test('.should select reviewer node itself', t => {
    const searchResult = {
      potentialReviewers: [POTENTIAL_REVIEWER_1]
    }

    const { nodesByClass, nodeByPersonId, graph, node } = createGraphTester(searchResult);

    t.equal(nodesByClass(SELECTED_NODE_CLASS).size(), 0);
    selectNodeByNode(node, nodeByPersonId(PERSON_ID_1));
    t.equal(nodesByClass(SELECTED_NODE_CLASS).size(), 1);

    t.end();
  });

  g.test('.should not select reviewer node if null', t => {
    const { nodesByClass, nodeByPersonId, graph, node } = createGraphTester(
      SEARCH_RESULT_WITH_POTENTIAL_REVIEWER
    );

    t.equal(nodesByClass(SELECTED_NODE_CLASS).size(), 0);
    selectNodeByNode(node, null);
    t.equal(nodesByClass(SELECTED_NODE_CLASS).size(), 0);

    t.end();
  });

  g.test('.should not select manuscripts reviewer is not corresponding author of', t => {
    const { nodesByClass, nodeByPersonId, graph, node } = createGraphTester(
      SEARCH_RESULT_WITH_NON_CORRESPONDING_AUTHOR
    );

    t.equal(nodesByClass(MANUSCRIPT_OF_CORRESPONDING_AUTHOR_CLASS).size(), 0);
    selectNodeByNode(node, nodeByPersonId(PERSON_ID_1));
    t.equal(nodesByClass(MANUSCRIPT_OF_CORRESPONDING_AUTHOR_CLASS).size(), 0);

    t.end();
  });

  g.test('.should select manuscripts reviewer is corresponding author of', t => {
    const { nodesByClass, nodeByPersonId, graph, node } = createGraphTester(
      SEARCH_RESULT_WITH_CORRESPONDING_AUTHOR
    );

    t.equal(nodesByClass(MANUSCRIPT_OF_CORRESPONDING_AUTHOR_CLASS).size(), 0);
    selectNodeByNode(node, nodeByPersonId(PERSON_ID_1));
    t.equal(nodesByClass(MANUSCRIPT_OF_CORRESPONDING_AUTHOR_CLASS).size(), 1);

    t.end();
  });

  g.test('.should not select corresponding authors if not corresponding author', t => {
    const { nodesByClass, nodeByManuscriptId, graph, node } = createGraphTester(
      SEARCH_RESULT_WITH_NON_CORRESPONDING_AUTHOR
    );

    t.equal(nodesByClass(CORRESPONDING_AUTHOR_CLASS).size(), 0);
    selectNodeByNode(node, nodeByManuscriptId(MANUSCRIPT_ID_1), graph.nodes);
    t.equal(nodesByClass(CORRESPONDING_AUTHOR_CLASS).size(), 0);

    t.end();
  });

  g.test('.should select corresponding authors of manuscripts', t => {
    const { nodesByClass, nodeByManuscriptId, graph, node } = createGraphTester(
      SEARCH_RESULT_WITH_CORRESPONDING_AUTHOR
    );

    t.equal(nodesByClass(CORRESPONDING_AUTHOR_CLASS).size(), 0);
    selectNodeByNode(node, nodeByManuscriptId(MANUSCRIPT_ID_1), graph.nodes);
    t.equal(nodesByClass(CORRESPONDING_AUTHOR_CLASS).size(), 1);

    t.end();
  });
});
