import React from 'react';
import ResizeObserver from 'resize-observer-polyfill';

import * as d3 from 'd3';
import d3Tip from 'd3-tip';
import Set from 'es6-set';
import sortOn from 'sort-on';

import {
  formatCombinedScore,
  formatScoreWithDetails
} from './formatUtils';


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

const escapeHtml = s => {
  const div = document.createElement('div');
  div.appendChild(document.createTextNode(s));
  return div.innerHTML;
}

const getManuscriptTooltipHtml = m => {
  let s = '<p class="title">' +
    '<b>title:</b> ' +
    escapeHtml(m.title) +
  '</p>';
  if (m.score && m.score.combined) {
    s += '<p class="score">' +
      '<b>score:</b> ';
    s += formatScoreWithDetails(m.score);
    s += '</p>';
  }
  if (m.abstract) {
    s += '<p class="abstract">' +
      '<b>abstract:</b> ' +
      escapeHtml(m.abstract) +
    '</p>';
  }
  return s;
}

const getReviewerTooltipHtml = r => {
  const p = r['person'];
  let s = '<p class="person-name">' +
    escapeHtml(p['first_name'] + ' ' + p['last_name']) +
  '</p>';
  if (p['institution']) {
    s += '<p class="person-institution">' +
      escapeHtml(p['institution']) +
    '</p>';
  }
  if (r.scores && r.scores.combined) {
    s += '<p class="score">' +
      '<b>score:</b> ';
    s += formatScoreWithDetails(r.scores);
    s += '</p>';
  }
  return s;
}

const getTooltipHtml = d => {
  let s = '<div class="tooltip">';
  if (d.manuscript) {
    s += getManuscriptTooltipHtml(d.manuscript);
  } else if (d.potentialReviewer) {
    s += getReviewerTooltipHtml(d.potentialReviewer);
  }
  s += '</div>';
  return s;
}

const createTooltip = () => {
  const tip = d3Tip()
    .attr('class', 'd3-tip')
    .offset([-10, 0])
    .html(getTooltipHtml);
  return tip;
}

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

const linkOpacity = d => {
  const singleScore = asSingleScore(d.score);
  const minOpacity = 0.5;
  return Math.min(1,
    minOpacity + (1 - minOpacity) * singleScore
  );
}

const linkDistance = link => {
  const minDistance = 10;
  const maxDistance = 100;
  const singleScore = asSingleScore(link.score);
  const distance = minDistance + (1 - singleScore) * (maxDistance - minDistance);
  console.log("singleScore:", singleScore, ", distance:", distance);
  return distance;
}

const linkStrength = link => {
  const minStrength = 0.1;
  const maxStrength = 0.7;
  const singleScore = asSingleScore(link.score);
  const strength = minStrength + (1 - singleScore) * (maxStrength - minStrength);
  console.log("singleScore:", singleScore, ", strength:", strength);
  return strength;
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

const nodeScoreEndAngle = d => {
  const singleScore = nodeSingleScore(d);
  if (singleScore > 0 && !d.isMain) {
    return Math.min(2 * Math.PI, 2 * Math.PI * singleScore);
  }
  return 0;
}

const createNode = (parent, nodes) => {
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

const createLegend = (parent, showSearch, options) => {
  const legend = parent.append("g")
    .style('opacity', 0.7)
    .attr('class', 'legend')
    .attr("transform", d => "translate(20, 20)");

  const backround = legend
    .append('rect')
    .attr('x', -10)
    .attr('y', -10)
    .attr('width', 205)
    .attr('fill', '#fff');

  const fullScore = {
    combined: 1
  };
  const legendData = [{
    isMain: true,
    label: showSearch ? 'Search' : 'Main manuscript',
    manuscript: {
    }
  }, {
    potentialReviewer: {
      person: {
      }
    },
    label: 'Potential reviewer'
  }, {
    potentialReviewer: {
      person: {
        stats: {
          overall: {
            'review_duration': {
              mean: 10
            }
          }
        },
      }
    },
    label: 'Potential reviewer\nwith review duration'
  }, {
    potentialReviewer: {
      person: {
      }
    },
    is_corresponding_author: true,
    label: 'Corresponding author\nof selected manuscript'
  }, {
    potentialReviewer: {
      person: {
        'is_early_career_researcher': true
      }
    },
    label: 'Early career reviewer'
  }];
  const includeOtherManuscripts = true;
  if (includeOtherManuscripts) {
    legendData.push({
      manuscript: {
      },
      label: (
        options.showAllRelatedManuscripts ?
        'Related manuscript' :
        'Common manuscript'
      )
    });
  }
  legendData.push({
    score: fullScore,
    label: 'Combined score\n(keyword & similarity)'
  });
  let currentY = 10;
  legendData.forEach((d, index) => {
    d.x = 10;
    d.y = currentY;
    d.labels = d.label.split('\n');
    currentY += 20 + d.labels.length * 20;
  });

  backround
    .attr('height', currentY - 10);

  const node = createNode(legend, legendData)
    .attr("transform", d => "translate(" + d.x + ", " + d.y + ")")
    .classed('node-corresponding-author', d => d.is_corresponding_author);
  for (let lineNo = 0; lineNo < 2; lineNo++) {
    node
      .append('text')
      .text(d => d.labels[lineNo])
      .attr('text-anchor', 'right')
      .attr("class", "legend-label")
      .attr("transform", d => "translate(20, " + (4 + 20 * lineNo) + ")");
  }
  return legend;
}


const initialiseNodePosition = (node, index, width, height) => {
  if (node.isMain || node.search) {
    node.fixed = true;
    node.fx = width / 2;
    node.fy = height / 2;
    return;
  }
  const t = (index / 10) * Math.PI * 2;
  const scale = 10 * index;
  node.x = (width / 2) + Math.cos(t) * scale;
  node.y = (height / 2) + Math.sin(t) * scale;
};

const updateParentSizeListener = (parent, svg) => () => {
  const width = parent.getBoundingClientRect().width;
  const height = parent.getBoundingClientRect().height;
  svg
    .attr("width", width)
    .attr("height", height);
}

const createLinksContainer = (parent, links) => parent.append("g")
  .attr("class", "links")
  .selectAll("line")
  .data(links)
  .enter();

const createLinkLine = parent => parent.append("line")
  .attr("stroke-width", d => d.width)
  .style('opacity', linkOpacity);

const addNodeDragBehavior = (node, simulation) => {
  const dragstarted = d => {
    if (!d3.event.active) {
      simulation.alphaTarget(0.3).restart();
    }
    d.fx = d.x;
    d.fy = d.y;
  }

  const dragged = d => {
    d.fx = d3.event.x;
    d.fy = d3.event.y;
  }

  const dragended = d => {
    if (!d3.event.active) {
      simulation.alphaTarget(0);
    }
    if (!d.fixed) {
      d.fx = null;
      d.fy = null;
    }
  }

  node.call(d3.drag()
    .on("start", dragstarted)
    .on("drag", dragged)
    .on("end", dragended));
  return node;
}

const addNodeTooltipBehavior = (node, tip) => node
  .on('mouseover', tip.show)
  .on('mouseout', tip.hide);


const addZoomContainer = parent => {
  const view = parent.append("g");

  var zoom = d3.zoom()
    .scaleExtent([0.1, 40])
    // .translateExtent([[-100, -100], [width + 90, height + 100]])
    .on("zoom", () => view.attr("transform", d3.event.transform));
  parent.call(zoom);

  return view;
}

const updateLinkLinePosition = line => line
  .attr("x1", d => d.source.x )
  .attr("y1", d => d.source.y )
  .attr("x2", d => d.target.x )
  .attr("y2", d => d.target.y );

const updateNodePosition = node => node
  .attr("transform", d => "translate(" + d.x + "," + d.y + ")");

const createChart = (parent, graph, options) => {
  const wrappedParent = d3.select(parent);

  const width = parent.getBoundingClientRect().width;
  const height = parent.getBoundingClientRect().height;

  const svg = wrappedParent
    .append("div")
    .classed("svg-container", true)
    .append("svg")
    .attr("width", width)
    .attr("height", height);

  graph.nodes.forEach((node, index) => initialiseNodePosition(node, index, width, height));

  var simulation = d3.forceSimulation()
    .force("link", d3.forceLink().id(d => d.id))
    .force("charge", d3.forceManyBody())
    // .force("center", d3.forceCenter(width / 2, height / 2))
    .force("collide", d3.forceCollide(20, 20));

  const updateSize = updateParentSizeListener(parent, svg);

  const windowResizeListener = updateSize;

  const ro = new ResizeObserver((entries, observer) => {
    updateSize();
  });

  ro.observe(parent);

  const tip = createTooltip();
  svg.call(tip);

  const view = addZoomContainer(svg);

  var link = createLinksContainer(view, graph.links);

  var line = createLinkLine(link);

  const node = createNode(view, graph.nodes);
  addNodeDragBehavior(node, simulation);
  addNodeTooltipBehavior(node, tip);

  const showSearch = !!graph.nodes[0].search;
  createLegend(svg, showSearch, options);

  const selectCorrespondingAuthorsOfNode = selectedNode => {
    const manuscript = selectedNode && selectedNode.manuscript;
    const authors = (manuscript && manuscript.authors) || [];
    const correspondingAuthors = authors.filter(author => author.is_corresponding_author);
    const correspondingAuthorPersonIds = new Set(
      correspondingAuthors.map(author => author.person_id)
    );
    console.log('correspondingAuthorPersonIds:', correspondingAuthorPersonIds);
    const isCorrespondingAuthor = d => {
      const person = d.potentialReviewer && d.potentialReviewer.person;
      const personId = person && person.person_id;
      return personId && correspondingAuthorPersonIds.has(personId);
    };
    node.classed('node-corresponding-author', isCorrespondingAuthor);
  };

  const manuscriptHasCorrespondingAuthor = (manuscript, personId) =>
    manuscript.authors
    .filter(author => author.person_id == personId && author.is_corresponding_author)
    .length > 0;

  const selectManuscriptsOfCorrespondingAuthorsNode = selectedNode => {
    const potentialReviewer = selectedNode && selectedNode.potentialReviewer;
    const person = potentialReviewer && potentialReviewer.person;
    const personId = person && person.person_id;
    const authorOf = (potentialReviewer && potentialReviewer.author_of_manuscripts) || [];
    const correspondingAuthorOf = authorOf.filter(
      m => manuscriptHasCorrespondingAuthor(m, personId)
    );
    const correspondingAuthorOfVersionIds = new Set(
      correspondingAuthorOf.map(m => m.version_id)
    );
    console.log('correspondingAuthorOfVersionIds:', correspondingAuthorOfVersionIds);
    const isManuscriptOfCorrespondingAuthor = d => {
      const versionId = d.manuscript && d.manuscript.version_id;
      return versionId && correspondingAuthorOfVersionIds.has(versionId);
    };
    node.classed('node-manuscript-of-corresponding-author', isManuscriptOfCorrespondingAuthor);
  };

  const selectNode = selectedNode => {
    console.log("select node:", selectedNode);
    const selectedId = selectedNode && selectedNode.id;
    const isSelected = d => d.id === selectedId;
    node.classed('selected', isSelected);
    selectCorrespondingAuthorsOfNode(selectedNode);
    selectManuscriptsOfCorrespondingAuthorsNode(selectedNode);
  }

  if (options.onNodeClicked) {
    node.on('click', options.onNodeClicked);
  }

  simulation
    .nodes(graph.nodes)
    .on("tick", () => {
      updateLinkLinePosition(line);
      updateNodePosition(node);
    });

  const force = simulation.force("link");
  force.links(graph.links)
  force.distance(linkDistance);
  // force.strength(linkStrength);

  const destroy = () => {
    window.removeEventListener('resize', windowResizeListener);
  }

  window.addEventListener('resize', windowResizeListener);
  return {
    destroy,
    selectNode
  };
};

class ChartResult extends React.Component {
  componentDidMount() {
    this.updateChart(this.props);
  }

  componentWillUnmount() {
    if (this.chart) {
      this.chart.destroy();
    }
  }

  shouldComponentUpdate() {
    return false;
  }

  updateChart(props) {
    const { searchResult, onNodeClicked } = props;
    if (searchResult) {
      const options = {
        showAllRelatedManuscripts: props.showAllRelatedManuscripts,
        maxRelatedManuscripts: props.maxRelatedManuscripts
      };
      const graph = recommendedReviewersToGraph(searchResult, options);
      if (this.chart) {
        this.chart.destroy();
      }
      this.chart = createChart(this.node, graph, {
        ...options,
        onNodeClicked
      });
      this.chart.selectNode(props.selectNode);
    }
  }

  componentWillReceiveProps(nextProps) {
    if (((nextProps.searchResult != this.props.searchResult) && (nextProps.searchResult)) ||
        (nextProps.showAllRelatedManuscripts != this.props.showAllRelatedManuscripts) ||
        (nextProps.maxRelatedManuscripts != this.props.maxRelatedManuscripts)) {
      this.updateChart(nextProps);
    } else if (this.chart && (nextProps.selectedNode != this.props.selectedNode)) {
      this.chart.selectNode(nextProps.selectedNode);
    }
  }

  render() {
    return <div ref={ ref => this.node = ref } className="chart-container"/>;
  }
}

export default ChartResult;
