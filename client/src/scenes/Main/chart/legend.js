import * as d3 from 'd3';

import {
  createNode
} from './node';

const FA_WINDOW_CLOSE_O_UNICODE = '\uf2d4';
const FA_QUESTION_UNICODE = '\uf128';

const doCreateOrUpdateLegend = (parent, options) => {
  let currentY = 10;

  const legendData = options.legendData;
  if (options.expanded) {
    legendData.forEach((d, index) => {
      d.x = 10;
      d.y = currentY;
      d.labels = d.label.split('\n');
      currentY += 20 + d.labels.length * 20;
    });
  } else {
    currentY += 30;
  }

  const content_width = options.expanded ? 175 : 20;
  const background_margin = 10;

  parent.selectAll('g').remove();

  const legend = parent.append("g").attr('class', 'legend-wrapper');

  // background
  legend
    .append('rect')
    .attr("class", "legend-background")
    .attr('x', -background_margin)
    .attr('y', -background_margin)
    .attr('width', content_width + 2 * background_margin)
    .attr('fill', '#fff')
    .attr('height', currentY - 10);
  
  // close button
  const legendCloseButton = legend
    .append('text')
    .attr('class', 'legend-close-button')
    .attr('font-family', 'FontAwesome')
    .attr('x', content_width - 15)
    .attr('y', 10)
    .text(d => options.expanded ? FA_WINDOW_CLOSE_O_UNICODE : FA_QUESTION_UNICODE)
    .on('click', () => options.onToggleExpand(options));

  if (options.expanded) {
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
  }

  return legend;
};
  
export const createLegend = (parent, showSearch, options) => {
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

  const legend = parent.append("g")
    .style('opacity', 0.7)
    .attr('class', 'legend')
    .attr("transform", d => "translate(20, 20)");

  doCreateOrUpdateLegend(
    legend, {
      ...options,
      legendData,
      expanded: true,
      onToggleExpand: state => doCreateOrUpdateLegend(
        legend, {
          ...state,
          expanded: !state.expanded
        }
      )
    }
  );

  return legend;
}
