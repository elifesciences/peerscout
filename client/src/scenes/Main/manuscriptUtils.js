import sortOn from 'sort-on';

import { groupByMultiple } from '../../utils';

const moveToFront = (list, item) => {
  if (list[0] == item) {
    // already at the front
    return list;
  }
  return [item].concat(
    list.filter(x => x !== item)
  );
};

const moveSelectPreferredManuscriptToFront = manuscripts => {
  if (manuscripts.length == 1) {
    return manuscripts;
  }
  const manuscriptsWithAbstract = manuscripts.filter(manuscript => !!manuscript.abstract);
  if (manuscriptsWithAbstract.length == 0) {
    return manuscripts;
  }
  const preferredManuscript = manuscriptsWithAbstract[0];
  return moveToFront(manuscripts, preferredManuscript);
};

export const duplicateManuscriptTitlesAsAlternatives = manuscripts => {
  if (!manuscripts || manuscripts.length < 2) {
    return manuscripts;
  }
  const manuscriptsByTitle = groupByMultiple(
    manuscripts.filter(manuscript => manuscript.title),
    manuscript => manuscript.title
  );
  Object.keys(manuscriptsByTitle).forEach(title => {
    manuscriptsByTitle[title] = moveSelectPreferredManuscriptToFront(
      manuscriptsByTitle[title]
    );
  });
  return manuscripts.map(manuscript => {
    const manuscriptsWithSameTitle = manuscriptsByTitle[manuscript.title];
    if (!manuscriptsWithSameTitle || manuscriptsWithSameTitle.length == 1) {
      return manuscript;
    }
    const preferredManuscript = manuscriptsWithSameTitle[0];
    if (manuscript == preferredManuscript) {
      return {
        ...manuscript,
        alternatives: manuscriptsWithSameTitle.slice(1)
      }
    } else {
      return null;
    }
  }).filter(manuscript => !!manuscript);
};

export const sortManuscriptsByPublishedTimestampDescending = manuscripts => manuscripts && sortOn(
  manuscripts,
  ['-published_timestamp', 'title']
);
