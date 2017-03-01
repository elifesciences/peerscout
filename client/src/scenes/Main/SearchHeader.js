import React from 'react';
import Headroom from 'react-headroom';

import {
  AutoComplete,
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

const BY_MANUSCRIPT = 'by-manuscript';
const BY_SEARCH = 'by-search';

class SearchHeader extends React.Component {
  constructor(props) {
    super(props);
    const { onSearchOptionsChanged, searchOptions: initialSearchOptions } = props;
    this.state = {
      currentTab: BY_MANUSCRIPT
    };
    this.state = this.getInitialiseState(initialSearchOptions);
    this.updateSearchOption = (key, value) => {
      const { currentTab } = this.state;
      const searchOptions = {
        ...this.state[currentTab],
        [key]: value
      };
      console.log("this.state[currentTab]:", this.state[currentTab], searchOptions);
      this.setState({
        [currentTab]: searchOptions
      });
      onSearchOptionsChanged(searchOptions);
    }
    this.handleTabChange = currentTab => {
      this.setState({
        currentTab
      });
    }
    this.onAbstractFocus = () => this.setState({ abstractFocused: true });
    this.onAbstractBlur = () => this.setState({ abstractFocused: false });
  }

  getInitialiseState(searchOptions) {
    if (searchOptions.manuscriptNumber) {
      return {
        currentTab: BY_MANUSCRIPT,
        [BY_MANUSCRIPT]: searchOptions
      }
    } else if (searchOptions.subjectArea || searchOptions.keywords) {
      return {
        currentTab: BY_SEARCH,
        [BY_SEARCH]: searchOptions
      }
    }
    return this.state;
  }

  componentWillReceiveProps(nextProps) {
    if (nextProps.searchOptions !== this.props.searchOptions) {
      this.setState(this.getInitialiseState(nextProps.searchOptions));
    }
  }
  
  render() {
    const { state, updateSearchOption, props } = this;
    const { allSubjectAreas=[] } = props;
    const { currentTab, abstractFocused } = state;
    const { manuscriptNumber } = (state[BY_MANUSCRIPT] || {});
    const { subjectArea, keywords, abstract } = (state[BY_SEARCH] || {});

    return (
      <Headroom>
        <Paper style={{ overflow: 'hidden' }}>
          <Tabs
            value={ currentTab }
            onChange={ this.handleTabChange }
          >
            <Tabs.Tab label="By Manuscript" value={ BY_MANUSCRIPT }>
              <View style={ styles.header }>
                <FlexRow>
                  <View style={ styles.inlineContainer }>
                    <FontAwesomeIcon style={{ paddingTop: 40 }} name="search"/>
                  </View>
                  <View style={ styles.field }>
                    <TextField
                      floatingLabelText="Manuscript number"
                      value={ manuscriptNumber || '' }
                      onChange={ (event, newValue) => updateSearchOption('manuscriptNumber', newValue) }
                      style={ styles.textField }
                    />
                  </View>
                </FlexRow>
              </View>
            </Tabs.Tab>
            <Tabs.Tab label="By Search Criteria" value={ BY_SEARCH }>
              <View style={ styles.header }>
                <FlexRow>
                  <View style={ styles.inlineContainer }>
                    <FontAwesomeIcon style={{ paddingTop: 40 }} name="search"/>
                  </View>
                  <View style={ styles.field }>
                    <AutoComplete
                      floatingLabelText="Subject area"
                      searchText={ subjectArea || '' }
                      onUpdateInput={ newValue => updateSearchOption('subjectArea', newValue) }
                      dataSource={ allSubjectAreas }
                      filter={ AutoComplete.fuzzyFilter }
                      style={ styles.textField }
                    />
                  </View>
                  <View style={ styles.field }>
                    <TextField
                      floatingLabelText="Keywords (comma separated)"
                      value={ keywords || '' }
                      onChange={ (event, newValue) => updateSearchOption('keywords', newValue) }
                      style={ styles.textField }
                    />
                  </View>
                  <View style={ styles.field }>
                    <TextField
                      floatingLabelText="Abstract"
                      multiLine={ true }
                      rowsMax={ 3 }
                      value={ abstract || '' }
                      onChange={ (event, newValue) => updateSearchOption('abstract', newValue) }
                      style={ styles.textField }
                      textareaStyle = { styles.textArea }
                      onFocus={ this.onAbstractFocus }
                      onBlur={ this.onAbstractBlur }
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
}

export default SearchHeader;
