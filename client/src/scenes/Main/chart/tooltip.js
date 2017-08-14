import d3Tip from 'd3-tip';

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

export const createTooltip = () => {
  const tip = d3Tip()
    .attr('class', 'd3-tip')
    .offset([-10, 0])
    .html(getTooltipHtml);
  return tip;
}

export const addNodeTooltipBehavior = (node, tip) => node
  .on('mouseover', tip.show)
  .on('mouseout', tip.hide);
