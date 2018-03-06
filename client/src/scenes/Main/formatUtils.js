export const formatScoreValue = value => Math.round(value * 100);

export const formatCombinedScore = combined => formatScoreValue(combined);

const formatKeywordScoreInline = keyword =>
  keyword ? formatScoreValue(keyword) + ' keyword match' : 'no keyword match';

const formatSimilarityScoreInline = similarity =>
  similarity ? formatScoreValue(similarity) + ' similarity' : '';

export const doiUrl = doi => doi && 'http://dx.doi.org/' + doi;

export const formatScoreDetails = ({ keyword, similarity }) =>
  [
    formatKeywordScoreInline(keyword),
    formatSimilarityScoreInline(similarity)
  ].filter(s => !!s).join(', ');

export const formatScoreWithDetails = score =>
  `${formatCombinedScore(score.combined)} (${formatScoreDetails(score)}) - out of 100`;

export const formatManuscriptId = manuscript => manuscript['manuscript_id'];

export const formatDate = date => date && new Date(date).toLocaleDateString();

export const formatPeriodNotAvailable = periodNotAvailable =>
`${formatDate(periodNotAvailable['start_date'])} - ${formatDate(periodNotAvailable['end_date'])}`;

export const formatCount = (count, singular, plural, suffix) =>
(count !== undefined) && `${count} ${count === 1 ? singular : plural} ${suffix || ''}`.trim();

export const quote = s => s && `\u201c${s}\u201d`;

export const personFullName = person => [
  person['first_name'],
  person['middle_name'],
  person['last_name']
].filter(s => !!s).join(' ');

const formatPersonStatus = status =>
  status && status.length > 0 ? status : 'Unknown status';

export const longPersonNameWithStatus = person =>
  [
    person['title'],
    person['first_name'],
    person['middle_name'],
    person['last_name'],
    person['is_early_career_researcher'] ? '(early career reviewer)': undefined,
    person['status'] !== 'Active' && `(${formatPersonStatus(person['status'])})`
  ].filter(s => !!s).join(' ');
