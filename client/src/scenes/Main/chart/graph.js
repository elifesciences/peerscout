import sortOn from 'sort-on';

const limit = (a, max) => a && max && a.length > max ? a.slice(0, max) : a;

const sortManuscriptsByScoreDescending = (manuscripts, scores) => {
  if (!manuscripts || (manuscripts.length < 2) || !scores || !scores.by_manuscript) {
    return manuscripts;
  }
  const scoreByVersionId = {};
  scores.by_manuscript.forEach(manuscript_scores => {
    scoreByVersionId[manuscript_scores.version_id] = manuscript_scores.combined;
  });
  const manuscriptsWithScores = manuscripts.map((manuscript, index) => ({
    score: scoreByVersionId[manuscript.version_id],
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

  const manuscriptToId = m => 'm' + m['manuscript_id'];
  const personToId = m => 'p' + m['person_id'];

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
    const manuscriptNo = manuscript && manuscript['manuscript_id'];
    const r = reviewerNode.potentialReviewer;
    if (manuscriptNo && r['scores'] && r['scores']['by_manuscript']) {
      const score = r['scores']['by_manuscript'].filter(
        s => s['manuscript_id'] === manuscriptNo
      )[0];
      link.score = score;
      if (score) {
        manuscript.score = score;
      }
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
    addReviewerManuscriptWithMinimumConnections(m, r, 1);

  const addCommonReviewerManuscript = (m, r) =>
    addReviewerManuscriptWithMinimumConnections(m, r, 2);

  const processReviewerLinks = linkProcessor => r => {
    const relatedManuscripts = limit(sortManuscriptsByScoreDescending(
      (r.author_of_manuscripts || []).concat(
        r.reviewer_of_manuscripts || []
      ),
      r.scores
    ), options.maxRelatedManuscripts);
    relatedManuscripts.forEach(m => linkProcessor(m, r));
  }

  const {
    matchingManuscripts,
    potentialReviewers,
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
      options.showAllRelatedManuscripts ?
      addAllReviewerManuscript :
      addCommonReviewerManuscript
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
