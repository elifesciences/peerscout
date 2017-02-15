import React from 'react';
import Tooltip from 'material-ui/internal/Tooltip';

import { View } from '../core';

const styles = {
  containerStyle: {
    maxWidth: 600
  },
  labelStyle: {
    whiteSpace: 'normal',
    lineHeight: 1.5,
    paddingTop: 5,
    paddingBottom: 5
  }
};

class TooltipWrapper extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      hoveredTooltip: false,
      hoverStyle: {
        ...this.containerStyle,
        left: 0,
        top: 0,
      }
    }
    this.handleMouseEnter = this.handleMouseEnter.bind(this);
    this.handleMouseLeave = this.handleMouseLeave.bind(this);
  }

  handleMouseEnter(event) {
    this.setState({
      hoveredTooltip: true,
      hoverStyle: {
        ...this.state.hoverStyle,
        left: event.pageX + 10,
        top: event.pageY + 10
      }
    });
  }

  handleMouseLeave(event) {
    this.setState({
      hoveredTooltip: false
    });
  }

  render() {
    const { content, children, style } = this.props;
    const label = (
      <View style={ styles.labelStyle }>
        { this.state.hoveredTooltip && content }
      </View>
    )
    return (
      <View
        onMouseEnter={ this.handleMouseEnter }
        onMouseLeave={ this.handleMouseLeave }
        style={ style }
      >
        { children }
        <Tooltip
          show={this.state.hoveredTooltip}
          style={ this.state.hoverStyle }
          label={ label }
          horizontalPosition="left"
          verticalPosition="top"
          touch={true}
          />
      </View>
    );
  }
}

export default TooltipWrapper;
