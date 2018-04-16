import * as d3 from 'd3';

import {
  formatCombinedScore,
  formatScoreWithDetails
} from '../formatUtils';

import {
  getPotentialReviewerCorrespondingAuthorVersionIdSet,
  getNodeVersionIdFilter,
  getManuscriptCorrespondingAuthorPersonIdSet,
  getNodePersonIdFilter,
  personToId
} from './graph';

export const SELECTED_NODE_CLASS = 'selected';
export const MANUSCRIPT_OF_CORRESPONDING_AUTHOR_CLASS = 'node-manuscript-of-corresponding-author';
export const CORRESPONDING_AUTHOR_CLASS = 'node-corresponding-author';

const nodeScore = d => (
  (d && d.score) ||
  (d && d.manuscript && d.manuscript.score) ||
  (d && d.potentialReviewer && d.potentialReviewer.scores)
);

const asSingleScore = score => (score && score.combined) || 0;

const nodeSingleScore = d => {
  if (d && d.isMain) {
    return 1;
  } else {
    return asSingleScore(nodeScore(d));
  }
}

const nodeOpacity = d => {
  const singleScore = nodeSingleScore(d);
  const minOpacity = 1;
  return Math.min(1,
    minOpacity + (1 - minOpacity) * singleScore
  );
}

const nodeStyleClass = d => {
  if (d.search) {
    return 'node-search';
  } else if (d.isMain) {
    return 'node-main-manuscript';
  } else if (d.manuscript) {
    return 'node-manuscript';
  } else if (d.potentialReviewer) {
    let s = 'node-potential-reviewer';
    if (d.potentialReviewer.person['is_early_career_researcher']) {
      s += ' node-early-career-researcher';
    }
    return s;
  } else {
    return 'node-unknown';
  }
};

const nodeImage = d => {
  if (d.potentialReviewer) {
    return '/images/person.svg';
  } else if (d.manuscript) {
    return '/images/manuscript.svg';
  }
}

export const nodeReviewDurationEndAngle = d => {
  if (d.potentialReviewer) {
    const p = d.potentialReviewer['person'];
    const stats = p.stats;
    const overall = stats && stats['overall'];
    const reviewDuration = overall && overall['review_duration'];
    const meanReviewDuration = reviewDuration && reviewDuration['mean'];
    if (meanReviewDuration > 0) {
      return Math.min(2 * Math.PI, 2 * Math.PI * meanReviewDuration / 50);
    }
  }
  return 0;
}

export const createNode = (parent, nodes) => {
  const nodeParent = parent.append("g")
    .attr("class", "nodes")
    .selectAll("circle")
    .data(nodes)
    .enter()
    .append('g')
    .attr("class", nodeStyleClass)
    .style('opacity', nodeOpacity);

  const node = nodeParent.append('g');
    
  node.append("circle")
    .attr("r", 15);

  node.append("svg:image")
   .attr('x',-11)
   .attr('y',-12)
   .attr('width', 20)
   .attr('height', 24)
   .attr("xlink:href", nodeImage)
   .style('opacity', 0.4);

  node.append("path")
    .attr("class", "reviewer-duration-indicator")
    .attr("d", d3.arc()
      .innerRadius(10)
      .outerRadius(15)
      .startAngle(0)
      .endAngle(nodeReviewDurationEndAngle)
    );

  node.append("text")
    .text(d => {
      const singleScore = nodeSingleScore(d);
      return (singleScore && !d.isMain && formatCombinedScore(singleScore)) || '';
    })
    .style("text-anchor", "middle")
    .attr("class", "node-text")
    .attr("transform", d => "translate(0, 6)");

  return nodeParent;
}

export const updateNodePosition = node => node
  .attr("transform", d => "translate(" + d.x + "," + d.y + ")");

export const selectManuscriptsOfCorrespondingAuthorsReviewer = (node, potentialReviewer) => {
  const correspondingAuthorOfVersionIds = getPotentialReviewerCorrespondingAuthorVersionIdSet(
    potentialReviewer
  );
  console.log('correspondingAuthorOfVersionIds:', correspondingAuthorOfVersionIds);
  node.classed(
    MANUSCRIPT_OF_CORRESPONDING_AUTHOR_CLASS,
    getNodeVersionIdFilter(correspondingAuthorOfVersionIds)
  );
};

export const selectManuscriptsOfCorrespondingAuthorsNode = (node, selectedNode) => {
  const potentialReviewer = selectedNode && selectedNode.potentialReviewer;
  selectManuscriptsOfCorrespondingAuthorsReviewer(node, potentialReviewer);
};

export const selectCorrespondingAuthorsOfManuscript = (node, manuscript, allNodes) => {
  const correspondingAuthorPersonIds = getManuscriptCorrespondingAuthorPersonIdSet(
    manuscript, allNodes
  );
  console.log('correspondingAuthorPersonIds:', correspondingAuthorPersonIds);
  node.classed(
    CORRESPONDING_AUTHOR_CLASS,
    getNodePersonIdFilter(correspondingAuthorPersonIds)
  );
};

export const selectCorrespondingAuthorsOfManuscriptNode = (node, selectedNode, allNodes) => {
  const manuscript = selectedNode && selectedNode.manuscript;
  selectCorrespondingAuthorsOfManuscript(node, manuscript, allNodes);
};

export const selectNodeById = (node, selectedId) => {
  console.log("select node id:", selectedId);
  const isSelected = d => d.id === selectedId;
  node.classed(SELECTED_NODE_CLASS, isSelected);
};

export const selectNodeByNode = (node, selectedNode, allNodes) => {
  selectNodeById(node, selectedNode && selectedNode.id);
  selectCorrespondingAuthorsOfManuscriptNode(node, selectedNode, allNodes);
  selectManuscriptsOfCorrespondingAuthorsNode(node, selectedNode);
};

export const selectNodeByReviewer = (node, selectedReviewer) => {
  console.log("selected reviewer:", selectedReviewer);
  const selectedPerson = selectedReviewer && selectedReviewer.person;
  selectNodeById(node, selectedPerson && personToId(selectedPerson));
  selectCorrespondingAuthorsOfManuscriptNode(node, null);
  selectManuscriptsOfCorrespondingAuthorsReviewer(node, selectedReviewer);    
};
