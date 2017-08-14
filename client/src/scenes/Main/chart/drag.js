import * as d3 from 'd3';

export const addNodeDragBehavior = (node, simulation) => {
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
