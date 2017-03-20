export const formatScoreValue = value => Math.round(value * 100);

export const formatCombinedScore = combined => formatScoreValue(combined);

const formatKeywordScoreInline = keyword =>
  keyword ? formatScoreValue(keyword) + ' keyword match' : 'no keyword match';

const formatSimilarityScoreInline = similarity =>
  similarity ? formatScoreValue(similarity) + ' similarity' : '';

const doiUrl = doi => doi && 'http://dx.doi.org/' + doi;

export const formatScoreDetails = ({ keyword, similarity }) =>
  [
    formatKeywordScoreInline(keyword),
    formatSimilarityScoreInline(similarity)
  ].filter(s => !!s).join(', ');

export const formatScoreWithDetails = score =>
  `${formatCombinedScore(score.combined)} (${formatScoreDetails(score)}) - out of 100`;
