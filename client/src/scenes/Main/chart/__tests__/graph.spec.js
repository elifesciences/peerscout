import test from 'tape';

import Set from 'es6-set';

import {
  recommendedReviewersToGraph,
  getPotentialReviewerCorrespondingAuthorVersionIdSet,
  getManuscriptCorrespondingAuthorPersonIdSet,
  getNodeVersionIdFilter,
  getNodePersonIdFilter
} from '../graph';

const MANUSCRIPT_NODE_PREFIX = 'm';
const PERSON_NODE_PREFIX = 'p';
const SEARCH_NODE_ID = 'search';

const MANUSCRIPT_ID_1 = '1001';
const MANUSCRIPT_ID_2 = '1002';
const MANUSCRIPT_ID_3 = '1003';

const VERSION_ID_1 = MANUSCRIPT_ID_1 + '-1';
const VERSION_ID_2 = MANUSCRIPT_ID_2 + '-1';
const VERSION_ID_3 = MANUSCRIPT_ID_3 + '-1';

const PERSON_ID_1 = 'person1';
const PERSON_ID_2 = 'person2';

const MANUSCRIPT_1 = {
  manuscript_id: MANUSCRIPT_ID_1,
  version_id: VERSION_ID_1,
  title: `Manuscript ${VERSION_ID_1}`
};

const MANUSCRIPT_2 = {
  manuscript_id: MANUSCRIPT_ID_2,
  version_id: VERSION_ID_2,
  title: `Manuscript ${VERSION_ID_2}`
};

const MANUSCRIPT_3 = {
  manuscript_id: MANUSCRIPT_ID_3,
  version_id: VERSION_ID_3,
  title: `Manuscript ${VERSION_ID_3}`
};

const PERSON_1 = {
  person_id: PERSON_ID_1,
};

test('graph.recommendedReviewersToGraph', g => {
  g.test('.should only include search node if no reviewers have been recommended', t => {
    const graph = recommendedReviewersToGraph({});
    t.deepEqual(graph.nodes.map(n => n.id), [SEARCH_NODE_ID]);
    t.deepEqual(graph.links, []);
    t.end();
  });

  g.test('.should only include main manuscript node without recommended reviewers', t => {
    const graph = recommendedReviewersToGraph({
      matchingManuscripts: [MANUSCRIPT_1]
    });
    t.deepEqual(graph.nodes.map(n => n.id), [MANUSCRIPT_NODE_PREFIX + MANUSCRIPT_ID_1]);
    t.deepEqual(graph.links, []);
    t.end();
  });

  g.test('.should include one reviewer node with no manuscripts', t => {
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

  g.test('.should include one reviewer node with one related manuscript', t => {
    const graph = recommendedReviewersToGraph({
      potentialReviewers: [{
        person: PERSON_1,
        related_manuscript_version_ids_by_relationship_type: {
          author: [VERSION_ID_1]
        }
      }],
      relatedManuscriptByVersionId: {
        [VERSION_ID_1]: MANUSCRIPT_1
      }
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

  g.test('.should add multiple related manuscripts', t => {
    const graph = recommendedReviewersToGraph({
      potentialReviewers: [{
        person: PERSON_1,
        related_manuscript_version_ids_by_relationship_type: {
          author: [VERSION_ID_1, VERSION_ID_2, VERSION_ID_3]
        }
      }],
      relatedManuscriptByVersionId: {
        [VERSION_ID_1]: MANUSCRIPT_1,
        [VERSION_ID_2]: MANUSCRIPT_2,
        [VERSION_ID_3]: MANUSCRIPT_3
      }
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


  g.test('.should not add alternative mauscript ids with same title', t => {
    const manuscriptWithSameTitle = {
      ...MANUSCRIPT_2,
      title: MANUSCRIPT_1.title
    };
    const graph = recommendedReviewersToGraph({
      potentialReviewers: [{
        person: PERSON_1,
        related_manuscript_version_ids_by_relationship_type: {
          author: [VERSION_ID_1, VERSION_ID_2]
        }
      }],
      relatedManuscriptByVersionId: {
        [VERSION_ID_1]: MANUSCRIPT_1,
        [VERSION_ID_2]: manuscriptWithSameTitle
      }
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
    t.end();
  });

  g.test('.should not add more than configured maximum related manuscripts', t => {
    const graph = recommendedReviewersToGraph({
      potentialReviewers: [{
        person: PERSON_1,
        related_manuscript_version_ids_by_relationship_type: {
          author: [VERSION_ID_1, VERSION_ID_2, VERSION_ID_3]
        }
      }],
      relatedManuscriptByVersionId: {
        [VERSION_ID_1]: MANUSCRIPT_1,
        [VERSION_ID_2]: MANUSCRIPT_2,
        [VERSION_ID_3]: MANUSCRIPT_3
      }
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

  g.test('.should sort related manuscripts and not add more than configured maximum', t => {
    const graph = recommendedReviewersToGraph({
      potentialReviewers: [{
        person: PERSON_1,
        related_manuscript_version_ids_by_relationship_type: {
          author: [VERSION_ID_1, VERSION_ID_2, VERSION_ID_3]
        }
      }],
      relatedManuscriptByVersionId: {
        [VERSION_ID_1]: {
          ...MANUSCRIPT_1,
          score: { combined: 0.9 }
        },
        [VERSION_ID_2]: {
          ...MANUSCRIPT_2,
          score: { combined: 0.7 }
        },
        [VERSION_ID_3]: {
          ...MANUSCRIPT_3,
          score: { combined: 0.8 }
        }
      }
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

test('graph.getPotentialReviewerCorrespondingAuthorVersionIdSet', g => {
  g.test('.should return empty set if no relationships are included', t => {
    const versionIds = Array.from(getPotentialReviewerCorrespondingAuthorVersionIdSet({
    })).sort();
    t.deepEqual(versionIds, []);
    t.end();
  });

  g.test('.should return empty set if no corresponding authors are included', t => {
    const versionIds = Array.from(getPotentialReviewerCorrespondingAuthorVersionIdSet({
      related_manuscript_version_ids_by_relationship_type: {}
    })).sort();
    t.deepEqual(versionIds, []);
    t.end();
  });

  g.test('.should return corresponding author version ids', t => {
    const versionIds = Array.from(getPotentialReviewerCorrespondingAuthorVersionIdSet({
      related_manuscript_version_ids_by_relationship_type: {
        corresponding_author: [VERSION_ID_1, VERSION_ID_2]
      }
    })).sort();
    t.deepEqual(versionIds, [VERSION_ID_1, VERSION_ID_2]);
    t.end();
  });
});

test('graph.getManuscriptCorrespondingAuthorPersonIdSet', g => {
  g.test('.should return empty set if manuscript is null', t => {
    const personIds = Array.from(getManuscriptCorrespondingAuthorPersonIdSet(null, [])).sort();
    t.deepEqual(personIds, []);
    t.end();
  });

  g.test('.should return empty set if manuscript has no version id', t => {
    const personIds = Array.from(getManuscriptCorrespondingAuthorPersonIdSet({
    }, [])).sort();
    t.deepEqual(personIds, []);
    t.end();
  });

  g.test('.should return person ids of corresponding authors', t => {
    const personIds = Array.from(getManuscriptCorrespondingAuthorPersonIdSet({
      version_id: VERSION_ID_1
    }, [{
      potentialReviewer: {
        person: {
          person_id: PERSON_ID_1,
        },
        related_manuscript_version_ids_by_relationship_type: {
          corresponding_author: [VERSION_ID_1]
        }
      }
    }])).sort();
    t.deepEqual(personIds, [PERSON_ID_1]);
    t.end();
  });
});

test('graph.getNodeVersionIdFilter', g => {
  g.test('.should return false if node is no manuscript', t => {
    t.false(getNodeVersionIdFilter(new Set())({}));
    t.end();
  });

  g.test('.should return false if manuscript has no version_id', t => {
    t.false(getNodeVersionIdFilter(new Set())({
      manuscript: {}
    }));
    t.end();
  });

  g.test('.should return false if manuscript version_id is not in set', t => {
    t.false(getNodeVersionIdFilter(new Set([VERSION_ID_2]))({
      manuscript: {
        version_id: VERSION_ID_1
      }
    }));
    t.end();
  });

  g.test('.should return true if manuscript version_id is in set', t => {
    t.true(getNodeVersionIdFilter(new Set([VERSION_ID_1]))({
      manuscript: {
        version_id: VERSION_ID_1
      }
    }));
    t.end();
  });
});

test('graph.getNodePersonIdFilter', g => {
  g.test('.should return false if node is no potential reviewer', t => {
    t.false(getNodePersonIdFilter(new Set())({}));
    t.end();
  });

  g.test('.should return false if potetial reviewer person id is not in set', t => {
    t.false(getNodePersonIdFilter(new Set([PERSON_ID_2]))({
      potentialReviewer: {
        person: {
          person_id: PERSON_ID_1
        }
      }
    }));
    t.end();
  });

  g.test('.should return true if potential reviewer person id in set', t => {
    t.true(getNodePersonIdFilter(new Set([PERSON_ID_1]))({
      potentialReviewer: {
        person: {
          person_id: PERSON_ID_1
        }
      }
    }));
    t.end();
  });
});
