import React from 'react';
import ResizeObserver from 'resize-observer-polyfill';

import * as d3 from 'd3';
import d3Tip from 'd3-tip';

import {
  formatCombinedScore,
  formatScoreWithDetails
} from './formatUtils';

const recommendedReviewersToGraph = recommendedReviewers => {
  const nodes = [];
  let links = [];
  const nodeMap = {};
  const linkMap = {};
  let mainManuscripts = [];
  let mainNodes = [];

  const manuscriptToId = m => 'm' + m['manuscript-no'];
  const personToId = m => 'p' + m['person-id'];

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
    const manuscriptNo = manuscript && manuscript['manuscript-no'];
    const r = reviewerNode.potentialReviewer;
    if (manuscriptNo && r['scores'] && r['scores']['by-manuscript']) {
      const score = r['scores']['by-manuscript'].filter(
        s => s['manuscript-no'] === manuscriptNo
      )[0];
      link.score = score;
      if (score) {
        manuscript.score = score;
      }
    }
  }

  const maxNodes = 50;

  const addManuscript = (m, r) => {
    const id = manuscriptToId(m);
    if (nodes.length > maxNodes) {
      // return;
    }
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
    if (nodes.length >= maxNodes) {
      return;
    }
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
    // if (r['author-of-manuscripts']) {
    //   r['author-of-manuscripts'].forEach(m => addManuscript(m, r));
    // }
    // if (r['reviewer-of-manuscripts']) {
    //   r['reviewer-of-manuscripts'].forEach(m => addManuscript(m, r));
    // }
    // mainManuscripts.forEach(m => {
    //   addManuscriptReviewerLink(m, r);
    // });
    mainNodes.forEach(mainNode => addReviewerLink(mainNode, node));
  }

  const addCommonReviewerManuscript = (m, r) => {
    const mid = manuscriptToId(m);
    if (nodeMap[mid]) {
      return;
    }
    // const pid = personToId(r['person']);
    const relatedPersons = (m['authors'] || []).concat(m['reviewers'] || []);
    const relatedPersonIds = relatedPersons.map(p => personToId(p));
    const reviewerPersonIds = relatedPersonIds.filter(personId => !!nodeMap[personId]);
    if (reviewerPersonIds.length > 1) {
      const manuscriptNode = addManuscript(m, r);
      reviewerPersonIds.forEach(personId => addReviewerLink(manuscriptNode, nodeMap[personId]));
    }
  }

  const addCommonReviewerLinks = r => {
    if (r['author-of-manuscripts']) {
      r['author-of-manuscripts'].forEach(m => addCommonReviewerManuscript(m, r));
    }
    if (r['reviewer-of-manuscripts']) {
      r['reviewer-of-manuscripts'].forEach(m => addCommonReviewerManuscript(m, r));
    }
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
    potentialReviewers.forEach(addCommonReviewerLinks);
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
    '<b>title:</b>' +
    escapeHtml(m.title) +
  '</p>';
  if (m.score && m.score.combined) {
    s += '<p class="score">' +
      '<b>score:</b> ';
    s += formatScoreWithDetails(m.score);
    s += '</p>';
  }
  s += '<p class="abstract">' +
    '<b>abstract:</b>' +
    escapeHtml(m.abstract) +
  '</p>';
  return s;
}

const getReviewerTooltipHtml = r => {
  const p = r['person'];
  let s = '<p class="person-name">' +
    escapeHtml(p['first-name'] + ' ' + p['last-name']) +
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

const nodeColor = d => {
  if (d.isMain || d.search) {
    return '#88f';
  } else if (d.manuscript) {
    return '#8cc';
  } else if (d.potentialReviewer) {
    if (d.potentialReviewer.person['is-early-career-researcher']) {
      return '#f88';
    }
    return '#8f8';
  } else {
    return '#fff';
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

const nodeReviewDurationEndAngle = d => {
  if (d.potentialReviewer) {
    const p = d.potentialReviewer['person'];
    const stats = p.stats;
    const last12m = stats && stats['last-12m'];
    const reviewDuration = last12m && last12m['review-duration'];
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
  var node = parent.append("g")
    .attr("class", "nodes")
    .selectAll("circle")
    .data(nodes)
    .enter()
    .append('g')
    .style('opacity', nodeOpacity);
    
  node.append("circle")
    .attr("r", 15)
    .attr("fill", nodeColor)

  node.append("svg:image")
   .attr('x',-11)
   .attr('y',-12)
   .attr('width', 20)
   .attr('height', 24)
   .attr("xlink:href", nodeImage)
   .style('opacity', 0.4);

  node.append("path")
    .style("fill", "#080")
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
    .style("fill", "#000")
    .style("text-anchor", "middle")
    .attr("class", "node-text")
    .attr("transform", d => "translate(0, 5)");

  return node;
}

const createLegend = (parent, showSearch) => {
  const legend = parent.append("g")
  .style('opacity', 0.7)
  .attr("transform", d => "translate(20, 20)");
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
          'last-12m': {
            'review-duration': {
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
        'is-early-career-researcher': true
      }
    },
    label: 'Early career researcher'
  }];
  const includeOtherManuscripts = true;
  if (includeOtherManuscripts) {
    legendData.push({
      manuscript: {
      },
      label: 'Common manuscript'
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
  const node = createNode(legend, legendData)
    .attr("transform", d => "translate(" + d.x + ", " + d.y + ")");
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
  const scale = 100 * (index * 10);
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
  createLegend(svg, showSearch);

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
    destroy
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
      const graph = recommendedReviewersToGraph(searchResult);
      if (this.chart) {
        this.chart.destroy();
      }
      this.chart = createChart(this.node, graph, {
        onNodeClicked 
      });
    }
  }

  componentWillReceiveProps(nextProps) {
    if ((nextProps.searchResult != this.props.searchResult) && (nextProps.searchResult)) {
      this.updateChart(nextProps);
    }
  }

  render() {
    return <div ref={ ref => this.node = ref } className="chart-container"/>;
  }
}

export default ChartResult;
