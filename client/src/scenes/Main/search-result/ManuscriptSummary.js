import React from 'react';

import {
  Card,
  CardHeader,
  CardText,
  FlexColumn,
  Text,
  View
} from '../../../components';

import ManuscriptRefLink from './ManuscriptRefLink';
import CorrespondingAuthorIndicator from './CorrespondingAuthorIndicator';

import {
  quote,
  longPersonNameWithStatus
} from '../formatUtils';

const LABEL_WIDTH = 105;

const styles = {
  manuscriptSummary: {
    container: {
      marginBottom: 10,
    },
    text: {
      fontSize: 20,
      fontWeight: 'bold'
    },
    subSection: {
      marginBottom: 5,
      marginLeft: LABEL_WIDTH
    },
    label: {
      display: 'inline-block',
      minWidth: LABEL_WIDTH,
      fontWeight: 'bold',
      marginLeft: -LABEL_WIDTH
    },
    abstractSubSection: {
      marginBottom: 5
    },
    abstractLabel: {
      display: 'inline-block',
      minWidth: 100,
      fontWeight: 'bold'
    }
  },
  inlineNonBlock: {
    display: 'inline'
  }
};


export const PersonInlineSummary = ({ person }) => (
  <Text>{ longPersonNameWithStatus(person) }</Text>
);

export const PersonListInlineSummary = ({ persons }) => (
  <View style={ styles.inlineNonBlock }>
    {
      persons && persons.map((person, index) => (
        <View key={ index } style={ styles.inlineNonBlock }>
          {
            index > 0 && (
              <Text>{ ', ' }</Text>
            )
          }
          <PersonInlineSummary person={ person }/>
          {
            person.is_corresponding_author && (
              <CorrespondingAuthorIndicator person={ person }/>
            )
          }
        </View>
      ))
    }
  </View>
);

export const ManuscriptSummary = ({ manuscript }) => {
  const {
    title,
    'manuscript_id': manuscriptNo,
    abstract,
    authors,
    reviewers,
    editors,
    'senior_editors': seniorEditors,
    'subject_areas': subjectAreas
  } = manuscript;
  return (
    <Card style={ styles.manuscriptSummary.container } initiallyExpanded={ true }>
      <CardHeader
        title={ quote(title) }
        subtitle={ <ManuscriptRefLink manuscript={ manuscript }/> }
        actAsExpander={ true }
        showExpandableButton={ true }
      />
      <CardText>
        <View style={ styles.manuscriptSummary.subSection }>
          <Text style={ styles.manuscriptSummary.label }>Authors: </Text>
          <PersonListInlineSummary persons={ authors }/>
        </View>
        {
          reviewers && reviewers.length > 0 && (
            <View  style={ styles.manuscriptSummary.subSection }>
              <Text style={ styles.manuscriptSummary.label }>Reviewers: </Text>
              <PersonListInlineSummary persons={ reviewers }/>
            </View>
          )
        }
        {
          editors && editors.length > 0 && (
            <View  style={ styles.manuscriptSummary.subSection }>
              <Text style={ styles.manuscriptSummary.label }>Editors: </Text>
              <PersonListInlineSummary persons={ editors }/>
            </View>
          )
        }
        {
          seniorEditors && seniorEditors.length > 0 && (
            <View  style={ styles.manuscriptSummary.subSection }>
              <Text style={ styles.manuscriptSummary.label }>Senior Editors: </Text>
              <PersonListInlineSummary persons={ seniorEditors }/>
            </View>
          )
        }
      </CardText>
      <CardText expandable={ true }>
        <View  style={ styles.manuscriptSummary.subSection }>
          <Text style={ styles.manuscriptSummary.label }>Subject areas:</Text>
          <Text>{ subjectAreas.join(', ') }</Text>
        </View>
        <View  style={ styles.manuscriptSummary.abstractSubSection }>
          <FlexColumn>
            <Text style={ styles.manuscriptSummary.abstractLabel }>Abstract:</Text>
            <Text>{ quote(abstract) }</Text>
          </FlexColumn>
        </View>
      </CardText>
    </Card>
  );
};

export default ManuscriptSummary;
