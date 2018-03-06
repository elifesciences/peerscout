import React from 'react';

import test from 'tape';
import { shallow, render } from 'enzyme';

import ManuscriptRefLink from '../ManuscriptRefLink';

import {
  formatManuscriptId,
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
    const component = render(<ManuscriptRefLink manuscript={ MANUSCRIPT } />);
    t.equal(component.text(), '' + formatManuscriptId(MANUSCRIPT));
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
