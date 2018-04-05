import React from 'react';

import test from 'tape';
import { shallow, render } from 'enzyme';

import ManuscriptRefLink from '../ManuscriptRefLink';

import {
  formatManuscriptDoi,
  doiUrl
} from '../../formatUtils';

const DOI = '10.123/test';

const MANUSCRIPT = {
  manuscript_id: '12345'
};

test('ManuscriptRefLink', g => {
  g.test('.should be defined', t => {
    t.true(ManuscriptRefLink);
    t.end();
  });

  g.test('.should render formatted manuscript id', t => {
    const manuscript = {...MANUSCRIPT, doi: DOI};
    const component = render(<ManuscriptRefLink manuscript={ manuscript } />);
    t.equal(component.text(), '' + formatManuscriptDoi(manuscript));
    t.end();
  });

  g.test('.should not populate href if no doi present', t => {
    const manuscript = {...MANUSCRIPT, doi: null};
    const component = shallow(<ManuscriptRefLink manuscript={ manuscript } />);
    t.false(component.props()['href']);
    t.end();
  });

  g.test('.should add doi link if present', t => {
    const manuscript = {...MANUSCRIPT, doi: DOI};
    const component = shallow(<ManuscriptRefLink manuscript={ manuscript } />);
    t.equal(component.props()['href'], doiUrl(DOI));
    t.end();
  });
});
