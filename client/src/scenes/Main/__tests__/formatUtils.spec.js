import test from 'tape';

import {
  formatManuscriptDoi
} from '../formatUtils';

const DOI = '10.123/test';

const MANUSCRIPT = {
  manuscript_id: '12345'
};

test('formatUtils.formatManuscriptDoi', g => {
  g.test('.should return doi if present', t => {
    const manuscript = {...MANUSCRIPT, doi: DOI};
    t.equal(formatManuscriptDoi(manuscript), DOI);
    t.end();
  });

  g.test('.should return fallback to manuscript id if doi is not present', t => {
    const manuscript = {...MANUSCRIPT, doi: null};
    t.equal(formatManuscriptDoi(manuscript), MANUSCRIPT.manuscript_id);
    t.end();
  });
});
