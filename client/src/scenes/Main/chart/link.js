import * as d3 from 'd3';

const asSingleScore = score => (score && score.combined) || 0;

const linkOpacity = d => {
  const singleScore = asSingleScore(d.score);
  const minOpacity = 0.5;
  return Math.min(1,
    minOpacity + (1 - minOpacity) * singleScore
  );
}

export const linkDistance = link => {
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


export const createLinksContainer = (parent, links) => parent.append("g")
  .attr("class", "links")
  .selectAll("line")
  .data(links)
  .enter();

export const createLinkLine = parent => parent.append("line")
  .attr("stroke-width", d => d.width)
  .style('opacity', linkOpacity);

export const updateLinkLinePosition = line => line
  .attr("x1", d => d.source.x)
  .attr("y1", d => d.source.y)
  .attr("x2", d => d.target.x)
  .attr("y2", d => d.target.y);
