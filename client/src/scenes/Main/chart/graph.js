import sortOn from 'sort-on';
import Set from 'es6-set';

import { flatMap } from '../../../utils';

import { duplicateManuscriptTitlesAsAlternatives } from '../manuscriptUtils';

export const manuscriptToId = m => 'm' + m['manuscript_id'];
export const personToId = p => 'p' + p['person_id'];

const limit = (a, max) => a && max && a.length > max ? a.slice(0, max) : a;

const sortManuscriptsByScoreDescending = manuscripts => {
  if (!manuscripts || (manuscripts.length < 2)) {
    return manuscripts;
  }
  const manuscriptsWithScores = manuscripts.map((manuscript, index) => ({
    score: manuscript.score && manuscript.score.combined,
    manuscript,
    index
  }));
  const sortedManuscriptsWithScores = sortOn(
    manuscriptsWithScores,
    ['-score', 'index']
  );
  return sortedManuscriptsWithScores.map(x => x.manuscript);
};

export const recommendedReviewersToGraph = (recommendedReviewers, options={}) => {
  const nodes = [];
  let links = [];
  const nodeMap = {};
  const linkMap = {};
  let mainManuscripts = [];
  let mainNodes = [];

  const addReviewerLink = (sourceNode, reviewerNode) => {
    const sourceId = sourceNode.id;
    const targetId = reviewerNode.id;
    if (!linkMap[sourceId]) {
      linkMap[sourceId] = {};
    }
    const reviewerLinksMap = linkMap[sourceId];
    if (reviewerLinksMap[targetId]) {
      return;
    }
    const link = {
      source: sourceId,
      target: targetId,
      value: 4
    };
    links.push(link);
    reviewerLinksMap[targetId] = link;

    const manuscript = sourceNode.manuscript;
    const r = reviewerNode.potentialReviewer;
    if (manuscript && manuscript.score) {
      link.score = manuscript.score;
    }
  }

  const addManuscript = (m, r) => {
    const id = manuscriptToId(m);
    if (nodeMap[id]) {
      return;
    }
    const node = {
      id,
      group: r ? 2 : 1,
      manuscript: m
    };
    nodeMap[id] = node;
    nodes.push(node);
    if (r) {
      addReviewerLink(node, nodeMap[personToId(r['person'])]);
    } else {
      node.isMain = true;
    }
    return node;
  }

  const addSearch = search => {
    const id = 'search';
    const node = {
      id,
      search: search
    };
    nodeMap[id] = node;
    nodes.push(node);
    return node;
  }

  const addReviewer = r => {
    const id = personToId(r['person']);
    if (nodeMap[id]) {
      return;
    }
    const node = {
      id,
      group: 3,
      potentialReviewer: r
    };
    nodeMap[id] = node;
    nodes.push(node);
    mainNodes.forEach(mainNode => addReviewerLink(mainNode, node));
  }

  const addReviewerManuscriptWithMinimumConnections = (m, r, minConnections) => {
    const mid = manuscriptToId(m);
    if (nodeMap[mid]) {
      return;
    }
    const relatedPersons = (m['authors'] || []).concat(m['reviewers'] || []);
    const relatedPersonIds = relatedPersons.map(p => personToId(p));
    const reviewerPersonIds = relatedPersonIds.filter(personId => !!nodeMap[personId]);
    if (reviewerPersonIds.length >= minConnections) {
      const manuscriptNode = addManuscript(m, r);
      reviewerPersonIds.forEach(personId => addReviewerLink(manuscriptNode, nodeMap[personId]));
    }
  }

  const addAllReviewerManuscript = (m, r) =>
    addReviewerManuscriptWithMinimumConnections(m, r, 0);

  const addCommonReviewerManuscript = (m, r) =>
    addReviewerManuscriptWithMinimumConnections(m, r, 2);

  const processReviewerLinks = (linkProcessor, relatedManuscriptByVersionId) => r => {
    const relatedManuscripts = limit(duplicateManuscriptTitlesAsAlternatives(
      sortManuscriptsByScoreDescending(
        flatMap(
          Object.keys(r.related_manuscript_version_ids_by_relationship_type || {}),
          key => r.related_manuscript_version_ids_by_relationship_type[key]
        ).map(versionId => relatedManuscriptByVersionId[versionId])
      )
    ), options.maxRelatedManuscripts);
    console.log('relatedManuscripts:', relatedManuscripts);
    relatedManuscripts.forEach(m => linkProcessor(m, r));
  }

  const {
    matchingManuscripts,
    potentialReviewers,
    relatedManuscriptByVersionId,
    search
  } = recommendedReviewers;

  console.log("search:", search);

  if (matchingManuscripts && matchingManuscripts.length > 0) {
    mainNodes = matchingManuscripts.map(addManuscript);
  } else {
    mainNodes = [addSearch(search)];
  }
  if (potentialReviewers) {
    potentialReviewers.forEach(addReviewer);
    potentialReviewers.forEach(processReviewerLinks(
      options.showAllRelatedManuscripts ? addAllReviewerManuscript : addCommonReviewerManuscript,
      relatedManuscriptByVersionId
    ));
  }

  // console.log("node keys:", Object.keys(nodeMap));
  // console.log("links before:", links);
  const linksBefore = links;
  links = links.filter(link =>
    nodeMap[link.source] && nodeMap[link.target]
  );
  // console.log("links:", links);
  console.log("links size:", linksBefore.length, links.length);

  console.log("nodes:", nodes);

  console.log("recommendedReviewers:", recommendedReviewers);

  return {
    nodes,
    links
  }
}

const getPotentialReviewerCorrespondingAuthorVersionIds = potentialReviewer => {
  const related_manuscript_version_ids_by_relationship_type = (
    potentialReviewer && potentialReviewer.related_manuscript_version_ids_by_relationship_type
  );
  return (
    related_manuscript_version_ids_by_relationship_type &&
    related_manuscript_version_ids_by_relationship_type.corresponding_author
  );
};

export const getPotentialReviewerCorrespondingAuthorVersionIdSet = potentialReviewer => (
  new Set(getPotentialReviewerCorrespondingAuthorVersionIds(potentialReviewer))
);

// Note: fairly slow implementation scanning all other nodes
const potentialReviewerHasCorrespondingAuthorVersionIds = (potentialReviewer, versionId) => (
  getPotentialReviewerCorrespondingAuthorVersionIdSet(potentialReviewer).has(versionId)
);

export const getManuscriptCorrespondingAuthorPersonIdSet = (manuscript, allNodes) => {
  if (!manuscript || !manuscript.version_id || !allNodes.length) {
    return new Set();
  }
  return new Set(
    allNodes.filter(
      node => potentialReviewerHasCorrespondingAuthorVersionIds(
        node.potentialReviewer, manuscript.version_id
      )
    ).map(node => node.potentialReviewer.person.person_id)
  );
};

export const getNodeVersionIdFilter = versionIdSet => d => {
  const versionId = d.manuscript && d.manuscript.version_id;
  return versionId && versionIdSet.has(versionId);
};

export const getNodePersonIdFilter = personIdSet => d => {
  const personId = d.potentialReviewer && d.potentialReviewer.person.person_id;
  return personId && personIdSet.has(personId);
};
