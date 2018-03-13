import test from 'tape';

import {
  duplicateManuscriptTitlesAsAlternatives,
  sortManuscriptsByPublishedTimestampDescending
} from '../manuscriptUtils';

const MANUSCRIPT_1 = {
  version_id: 'm1-1',
  title: 'Manuscript 1'
};

const MANUSCRIPT_2 = {
  version_id: 'm2-1',
  title: 'Manuscript 2'
};

const MANUSCRIPT_3 = {
  version_id: 'm3-1',
  title: 'Manuscript 3'
};

test('manuscriptUtils.duplicateManuscriptTitlesAsAlternatives', g => {
  g.test('.should return empty list if input is empty', t => {
    t.deepEqual(duplicateManuscriptTitlesAsAlternatives([]), []);
    t.end();
  });

  g.test('.should return unchanged manuscript list with different titles', t => {
    t.deepEqual(duplicateManuscriptTitlesAsAlternatives([
      MANUSCRIPT_1, MANUSCRIPT_2, MANUSCRIPT_3
    ]), [MANUSCRIPT_1, MANUSCRIPT_2, MANUSCRIPT_3]);
    t.end();
  });

  g.test('.should retain order of manuscripts', t => {
    t.deepEqual(duplicateManuscriptTitlesAsAlternatives([
      MANUSCRIPT_3, MANUSCRIPT_1, MANUSCRIPT_2
    ]), [MANUSCRIPT_3, MANUSCRIPT_1, MANUSCRIPT_2]);
    t.end();
  });

  g.test('.should retain order of manuscripts without title', t => {
    const manuscriptsWithoutTitle = [{
      ...MANUSCRIPT_2,
      title: null
    }, {
      ...MANUSCRIPT_1,
      title: null
    }];
    t.deepEqual(duplicateManuscriptTitlesAsAlternatives(
      manuscriptsWithoutTitle
    ), manuscriptsWithoutTitle);
    t.end();
  });

  g.test('.should return manuscript with same title as alternative', t => {
    const manuscriptWithSameTitle = {
      ...MANUSCRIPT_2,
      title: MANUSCRIPT_1.title
    };
    t.deepEqual(duplicateManuscriptTitlesAsAlternatives([
      MANUSCRIPT_1, manuscriptWithSameTitle
    ]), [{
      ...MANUSCRIPT_1,
      alternatives: [manuscriptWithSameTitle]
    }]);
    t.end();
  });

  g.test('.should prefer manuscript with abstract', t => {
    const manuscriptWithoutAbstract = {
      ...MANUSCRIPT_1,
      abstract: null
    };
    const manuscriptWithSameTitleAndAbstract = {
      ...MANUSCRIPT_2,
      title: MANUSCRIPT_1.title,
      abstract: 'abstract matters'
    };
    t.deepEqual(duplicateManuscriptTitlesAsAlternatives([
      manuscriptWithoutAbstract, manuscriptWithSameTitleAndAbstract
    ]), [{
      ...manuscriptWithSameTitleAndAbstract,
      alternatives: [manuscriptWithoutAbstract]
    }]);
    t.end();
  });
});

test('manuscriptUtils.sortManuscriptsByPublishedTimestampDescending', g => {
  g.test('.should not fail on undefined array', t => {
    t.deepEqual(
      sortManuscriptsByPublishedTimestampDescending(undefined),
      undefined
    )
    t.end();
  });

  g.test('.should sort manuscripts by published_timestamp', t => {
    const manuscript_1 = {
      ...MANUSCRIPT_1,
      published_timestamp: '2017-01-01T00:00:00'
    };
    const manuscript_2 = {
      ...MANUSCRIPT_2,
      published_timestamp: '2017-01-02T00:00:00'
    };
    t.deepEqual(
      sortManuscriptsByPublishedTimestampDescending([manuscript_1, manuscript_2]),
      [manuscript_2, manuscript_1]
    )
    t.end();
  });

  g.test('.should move absent published_timestamp to the end', t => {
    const manuscript_1 = {
      ...MANUSCRIPT_1,
      published_timestamp: undefined
    };
    const manuscript_2 = {
      ...MANUSCRIPT_2,
      published_timestamp: '2017-01-02T00:00:00'
    };
    t.deepEqual(
      sortManuscriptsByPublishedTimestampDescending([manuscript_1, manuscript_2]),
      [manuscript_2, manuscript_1]
    )
    t.end();
  });

  g.test('.should sort manuscripts by title second', t => {
    const manuscript_1 = {
      ...MANUSCRIPT_1,
      published_timestamp: '2017-01-01T00:00:00',
      title: 'B'
    };
    const manuscript_2 = {
      ...MANUSCRIPT_2,
      published_timestamp: '2017-01-01T00:00:00',
      title: 'A'
    };
    t.deepEqual(
      sortManuscriptsByPublishedTimestampDescending([manuscript_1, manuscript_2]),
      [manuscript_2, manuscript_1]
    )
    t.end();
  });


  g.test('.should move undefined title to the end', t => {
    const manuscript_1 = {
      ...MANUSCRIPT_1,
      published_timestamp: '2017-01-01T00:00:00',
      title: undefined
    };
    const manuscript_2 = {
      ...MANUSCRIPT_2,
      published_timestamp: '2017-01-01T00:00:00',
      title: 'A'
    };
    t.deepEqual(
      sortManuscriptsByPublishedTimestampDescending([manuscript_1, manuscript_2]),
      [manuscript_2, manuscript_1]
    )
    t.end();
  });
});
