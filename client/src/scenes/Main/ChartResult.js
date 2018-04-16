import React from 'react';
import ResizeObserver from 'resize-observer-polyfill';

import * as d3 from 'd3';
import Set from 'es6-set';

import {
  addNodeDragBehavior,
  personToId,
  recommendedReviewersToGraph,
  createLegend,
  createLinksContainer,
  createLinkLine,
  linkDistance,
  updateLinkLinePosition,
  createNode,
  updateNodePosition,
  createTooltip,
  addNodeTooltipBehavior,
  selectNodeByNode,
  selectNodeByReviewer
} from './chart';


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

const addZoomContainer = parent => {
  const view = parent.append("g");

  var zoom = d3.zoom()
    .scaleExtent([0.1, 40])
    // .translateExtent([[-100, -100], [width + 90, height + 100]])
    .on("zoom", () => view.attr("transform", d3.event.transform));
  parent.call(zoom);

  return view;
}

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
  const legend = createLegend(svg, showSearch, options);
  const { setLegendOpen } = legend;

  const selectNode = selectedNode => selectNodeByNode(node, selectedNode, graph.nodes);
  const selectedReviewer = selectedReviewer => selectNodeByReviewer(node, selectedReviewer);

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
    svg.remove();
  }

  window.addEventListener('resize', windowResizeListener);
  return {
    destroy,
    selectNode,
    selectedReviewer,
    setLegendOpen
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
        maxRelatedManuscripts: props.maxRelatedManuscripts,
        legendOpen: props.legendOpen,
        onOpenLegend: props.onOpenLegend,
        onCloseLegend: props.onCloseLegend
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
    } else if (this.chart && (nextProps.selectedReviewer != this.props.selectedReviewer)) {
      this.chart.selectedReviewer(nextProps.selectedReviewer);
    } else if (this.chart && (nextProps.legendOpen != this.props.legendOpen)) {
      this.chart.setLegendOpen(nextProps.legendOpen);
    }
  }

  render() {
    return <div ref={ ref => this.node = ref } className="chart-container"/>;
  }
}

export default ChartResult;
