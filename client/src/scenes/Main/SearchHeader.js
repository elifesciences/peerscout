import React from 'react';

import {
  AutoComplete,
  Chip,
  FlexColumn,
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
  },
  keywordList: {
    maxWidth: 300,
    flexWrap: 'wrap'
  },
  chip: {
    marginRight: 4,
    marginBottom: 4
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

    this.addKeyword = keyword => {
      const normalisedKeyword = keyword.trim().toLowerCase();
      const keywords = this.state.keywords || [];
      if (normalisedKeyword.length > 0 && keywords.indexOf(normalisedKeyword) < 0) {
        console.log("addKeyword:", keyword);
        const updatedKeywords = keywords.concat([normalisedKeyword]);
        updatedKeywords.sort();
        this.setState({
          currentKeyword: '',
          keywords: updatedKeywords
        });
        this.updateSearchOption('keywords', updatedKeywords.join(','));
      }
    }

    this.deleteKeyword = keyword => {
      const keywords = this.state.keywords || [];
      if (keywords.indexOf(keyword) >= 0) {
        console.log("deleteKeyword:", keyword);
        const updatedKeywords = keywords.filter(k => k !== keyword);
        this.setState({
          keywords: updatedKeywords
        });
        this.updateSearchOption('keywords', updatedKeywords.join(','));
      }
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
        keywords: (
          searchOptions.keywords &&
          searchOptions.keywords.length > 0 &&
          searchOptions.keywords.split(',').map(k => k.trim())
        ),
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
    const { allSubjectAreas=[], allKeywords=[] } = props;
    const {
      currentTab, abstractFocused,
      currentSubjectArea='', currentKeyword='', keywords=[]
    } = state;
    const { manuscriptNumber } = (state[BY_MANUSCRIPT] || {});
    const { subjectArea, abstract } = (state[BY_SEARCH] || {});

    return (
      <Paper style={{ overflow: 'hidden' }} zDepth={ 2 }>
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
                    searchText={ currentSubjectArea || subjectArea || '' }
                    onUpdateInput={ newValue => this.setState({currentSubjectArea: newValue}) }
                    onNewRequest={ newValue => updateSearchOption('subjectArea', newValue) }
                    dataSource={ allSubjectAreas }
                    filter={ AutoComplete.fuzzyFilter }
                    style={ styles.textField }
                  />
                </View>
                <View style={ styles.field }>
                  <FlexColumn>
                    <AutoComplete
                      floatingLabelText="Keywords"
                      searchText={ currentKeyword }
                      onUpdateInput={ newValue => this.setState({currentKeyword: newValue}) }
                      onNewRequest={ newValue => this.addKeyword(newValue) }
                      dataSource={ allKeywords }
                      filter={ AutoComplete.defaultFilter }
                      maxSearchResults={ 10 }
                      style={ styles.textField }
                    />
                    <FlexRow style={ styles.keywordList }>
                      {
                        keywords.map(keyword => (
                          <Chip
                            key={ keyword }
                            onRequestDelete={ () => this.deleteKeyword(keyword) }
                            style={ styles.chip }
                          >
                            { keyword }
                          </Chip>
                        ))
                      }
                    </FlexRow>
                  </FlexColumn>
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
    );
  }
}

export default SearchHeader;
