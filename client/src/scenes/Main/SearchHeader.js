import React from 'react';
import Headroom from 'react-headroom';

import {
  FlexRow,
  FontAwesomeIcon,
  Paper,
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
    backgroundColor: '#fff',
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
      </Paper>
    </Headroom>
  );
}

export default SearchHeader;
