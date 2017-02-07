import React from 'react';
import Dropzone from 'react-dropzone';

import {
  Text,
  View
} from '../core';

import {
  FlatButton,
} from '../material';

import {
  FontAwesomeIcon,
} from '../icons';

import { flatMap, readFileAsText } from '../../utils';

const baseStyles = {
  dropZone: {
    borderColor: '#ccc',
    borderStyle: 'dashed',
    borderWidth: 2,
    minWidth: 200,
    maxWidth: 200,
    minHeight: 50,
    padding: 10
  }
}

const styles = {
  container: {
    position: 'relative'
  },
  overlay: {
    position: 'absolute',
    padding: 10
  },
  button: {
    minWidth: 30,
    height: 30,
    lineHeight: 1
  },
  fileList: {
    paddingTop: 4,
    paddingLeft: 30
  },
  dropZone: baseStyles.dropZone,
  activeDropZone: {
    ...baseStyles.dropZone,
    borderColor: '#88c',
    backgroundColor: '#ccf'
  }
};

const findStringValues = value => {
  if (typeof value === "string") {
    return [value];
  } else if (Array.isArray(value)) {
    return flatMap(value, findStringValues);
  } else if (typeof value === "object") {
    return flatMap(Object.keys(value), key => findStringValues(value[key]));
  } else {
    return [];
  }
}

const parseJsonAndReturnText = s => findStringValues(JSON.parse(s)).join('\n');

class FileInput extends React.Component {
  constructor(props) {
    super(props);
    this.onLoadFile = file => {
      const isJson = file.name.toLowerCase().endsWith('.json');
      readFileAsText(file).then(text =>
        isJson ? parseJsonAndReturnText(text) : text
      ).then(text => {
        if (props.onLoad) {
          props.onLoad({
            name: file.name,
            data: text
          });
        }
      });
    }

    this.onDropFiles = files => {
      this.onLoadFile(files[0]);
    };

    this.onClear = event => {
      if (props.onLoad) {
        props.onLoad();
      }
    }
  }

  render() {
    const { file } = this.props;
    return (
      <View style={ styles.container }>
        { file &&
          <View style={ styles.overlay }>
            <FlatButton style={ styles.button } onClick={ this.onClear }>
              <FontAwesomeIcon name="times-circle-o"/>
            </FlatButton>
          </View>
        }
        <Dropzone
          style={ styles.dropZone }
          activeStyle={ styles.activeDropZone }
          onDrop={ this.onDropFiles }
        >
          { file &&
            (
              <View style={ styles.fileList }>
                <Text>{ file.name }</Text>
              </View>
            )
          }
          { !file &&
            <Text>Try dropping a JSON or text file here, or click to select a file.</Text>
          }
        </Dropzone>
      </View>
    );
  }
}

export default FileInput;
