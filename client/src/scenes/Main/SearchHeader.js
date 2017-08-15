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
  container: {
    overflow: 'hidden',
    zIndex: 1
  },
  field: {
    marginLeft: 20
  },
  info: {
    marginLeft: 20,
    marginTop: 20,
    color: '#888',
    fontSize: 12
  },
  subjectAreaOrKeywordsRequired: {
    color: '#f00'
  },
  inlineContainer: {
    display: 'inline-block'
  },
  header: {
    paddingTop: 0,
    paddingLeft: 8,
    paddingRight: 8,
    paddingBottom: 8,
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
};

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
        ) || [],
        [BY_SEARCH]: searchOptions
      }
    }
    return {
      currentTab: this.state.currentTab
    };
  }

  componentWillReceiveProps(nextProps) {
    if (nextProps.searchOptions !== this.props.searchOptions) {
      this.setState(this.getInitialiseState(nextProps.searchOptions));
    }
  }

  updateManuscriptNumber(value) {
    const m = /^.*\D(\d{5}$)/.exec(value);
    const manuscriptNumber = m ? m[1] : value;
    this.updateSearchOption('manuscriptNumber', manuscriptNumber);
  }

  forceUpdateSearchOptions = () => {
    const { onSearchOptionsChanged } = this.props;
    const { currentTab } = this.state;
    const searchOptions = this.state[currentTab];
    onSearchOptionsChanged(searchOptions);
  }

  onKeyPress = event => {
    if (event.charCode === 13) {
      this.forceUpdateSearchOptions();
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
    const subjectAreaOrKeywordsRequired = (!subjectArea) && (keywords.length == 0) && (
      abstract
    );

    return (
      <Paper style={ styles.container } zDepth={ 2 }>
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
                    floatingLabelText="Manuscript number (last 5 digits)"
                    value={ manuscriptNumber || '' }
                    onChange={ (event, newValue) => this.updateManuscriptNumber(newValue) }
                    onKeyPress={ this.onKeyPress }
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
                    onClose={ () => updateSearchOption('subjectArea', currentSubjectArea || '') }
                    onKeyPress={ this.onKeyPress }
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
                      onKeyPress={ this.onKeyPress }
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
                <View style={ styles.info }>
                  <View style={ styles.note }>
                    <Text>
                    Note: search results by subject area or keyword may be improved when also searching by abstract (i.e. copying and pasting an abstract)
                    </Text>
                  </View>
                  {
                    subjectAreaOrKeywordsRequired && (
                      <View style={ styles.subjectAreaOrKeywordsRequired }>
                        <Text>
                          Subject area or keywords required.
                        </Text>
                      </View>
                    )
                  }
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
