import React, { Component } from 'react';
import PropTypes from 'prop-types';
import JobActions from '../../actions/JobListActions';

class TableSectionHeader extends Component {
  constructor(props) {
    super(props);
    this.state = {
      header: this.props.header,
    };
  }

  render() {
    const { header } = this.state;
    const divClass = JobActions.getTableSectionHeaderDivClass(header);
    const arrowClass = JobActions.getTableSectionHeaderArrowClass(header);
    const textClass = JobActions.getTableSectionHeaderTextClass(header);

    return (
      <div className={divClass}>
        <p className={textClass}>{header}</p>
        <div className={arrowClass} />
      </div>
    );
  }
}

TableSectionHeader.propTypes = {
  header: PropTypes.string,
};

TableSectionHeader.defaultProps = {
  header: '',
};

export default TableSectionHeader;
