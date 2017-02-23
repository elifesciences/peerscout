import React from 'react';
import ReactPortalTooltip from 'react-portal-tooltip'

import { View } from '../core';

const styles = {
  tooltip: {
    style: {
      background: 'rgba(0,0,0,.8)',
      color: '#ccc',
      padding: 10,
      paddingTop: 5,
      paddingBottom: 5,
      boxShadow: '5px 5px 3px rgba(0,0,0,.5)',
      maxWidth: 800,
      whiteSpace: 'normal',
      lineHeight: 1.5,
    },
    arrowStyle: {
      color: 'rgba(0,0,0,.8)',
      borderColor: false
    },
  }
};

let idCounter = 1;

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
    this.id = 'tooltip-' + idCounter++;
  }

  handleMouseEnter(event) {
    this.setState({
      hoveredTooltipNow: true,
      hoverStyle: {
        ...this.state.hoverStyle,
        left: event.pageX + 10,
        top: event.pageY + 10
      }
    });
    // bug in ReactPortalTooltip requires trigger to happen a bit later (could be 0ms)
    // but it is good to delay it anyway to not get into the way all the time
    setTimeout(() => {
      this.setState(state => ({
        ...state,
        hoveredTooltip: state.hoveredTooltipNow
      }));
    }, 300);
  }

  handleMouseLeave(event) {
    this.setState({
      hoveredTooltipNow: false,
      hoveredTooltip: false,
    });
  }

  render() {
    const { content, children, style } = this.props;
    const label = (
      <View style={ styles.labelStyle }>
        { content }
      </View>
    )
    return (
      <View
        onMouseEnter={ this.handleMouseEnter }
        onMouseLeave={ this.handleMouseLeave }
        style={ style }
        className={ this.state.hoveredTooltip ? 'tooltip-active' : 'tooltip-inactive' }
      >
        <View
          id={ this.id }
        >
          { children }
        </View>
        <ReactPortalTooltip
          active={this.state.hoveredTooltip}
          arrow="top"
          position="bottom"
          parent={ `#${this.id}` }
          style={ styles.tooltip }
          tooltipTimeout={ 100 }
        >
          { content }
        </ReactPortalTooltip>
      </View>
    );
  }
}

export default TooltipWrapper;
