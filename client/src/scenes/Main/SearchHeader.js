import React from 'react';
import Headroom from 'react-headroom';

import {
  FlexRow,
  FontAwesomeIcon,
  Paper,
  Tabs,
  Text,
  TextField,
  View
} from '../../components';

const styles = {
  field: {
    marginLeft: 20
  },
  inlineContainer: {
    display: 'inline-block'
  },
  header: {
    padding: 8,
    paddingTop: 0,
    marginTop: -10,
    overflow: 'hidden'
  }
}

const SearchHeader = ({searchOptions, onSearchOptionsChanged}) => {
  const updateSearchOption = (key, value) => {
    onSearchOptionsChanged({
      ...searchOptions,
      [key]: value
    });
  }

  const { manuscriptNumber, keywords } = searchOptions;

  return (
    <Headroom>
      <Paper style={{ overflow: 'hidden' }}>
        <Tabs>
          <Tabs.Tab label="By Manuscript">
            <View style={ styles.header }>
              <FlexRow>
                <View style={ styles.inlineContainer }>
                  <FontAwesomeIcon style={{ paddingTop: 40 }} name="search"/>
                </View>
                <View style={ styles.field }>
                  <TextField
                    floatingLabelText="Manuscript number"
                    value={ manuscriptNumber }
                    onChange={ (event, newValue) => updateSearchOption('manuscriptNumber', newValue) }
                    style={ styles.textField }
                  />
                </View>
              </FlexRow>
            </View>
          </Tabs.Tab>
          <Tabs.Tab label="By Search Criteria">
            <View style={ styles.header }>
              <FlexRow>
                <View style={ styles.inlineContainer }>
                  <FontAwesomeIcon style={{ paddingTop: 40 }} name="search"/>
                </View>
                <View style={ styles.field }>
                  <TextField
                    floatingLabelText="Keywords (comma separated)"
                    value={ keywords }
                    onChange={ (event, newValue) => updateSearchOption('keywords', newValue) }
                    style={ styles.textField }
                  />
                </View>
              </FlexRow>
            </View>
          </Tabs.Tab>
        </Tabs>
      </Paper>
    </Headroom>
  );
}

export default SearchHeader;
