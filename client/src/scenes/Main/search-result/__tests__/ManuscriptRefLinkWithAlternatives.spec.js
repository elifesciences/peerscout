import React from 'react';

import test from 'tape';
import { shallow } from 'enzyme';

import ManuscriptRefLinkWithAlternatives from '../ManuscriptRefLinkWithAlternatives';

const MANUSCRIPT = {
  manuscript_id: '12345'
};

test('ManuscriptRefLinkWithAlternatives', g => {
  g.test('.should be defined', t => {
    t.true(ManuscriptRefLinkWithAlternatives);
    t.end();
  });
  
  g.test('.should pass manuscript without alternatives to ManuscriptRefLink', t => {
    const component = shallow(<ManuscriptRefLinkWithAlternatives manuscript={ MANUSCRIPT } />);
    const linkComponent = component.find('ManuscriptRefLink');
    t.equal(linkComponent.length, 1);
    t.equal(linkComponent.props()['manuscript'], MANUSCRIPT);
    t.end();
  });

  g.test('.should pass manuscript with alternatives to ManuscriptRefLink', t => {
    const manuscript = {
      ...MANUSCRIPT,
      alternatives: [
        {...MANUSCRIPT, manuscript_id: 'alternative1'},
        {...MANUSCRIPT, manuscript_id: 'alternative2'}
      ]
    };
    const component = shallow(<ManuscriptRefLinkWithAlternatives manuscript={ manuscript } />);
    const linkComponent = component.find('ManuscriptRefLink');
    t.equal(linkComponent.length, 3);
    t.equal(linkComponent.at(0).props()['manuscript'], manuscript);
    t.equal(linkComponent.at(1).props()['manuscript'], manuscript.alternatives[0]);
    t.equal(linkComponent.at(2).props()['manuscript'], manuscript.alternatives[1]);
    t.end();
  });
});
