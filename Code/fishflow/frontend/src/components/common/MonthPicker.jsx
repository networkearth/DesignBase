import React from 'react';
import PropTypes from 'prop-types';
import CheckBoxPicker from './CheckBoxPicker';

const MonthPicker = ({
  selectedMonths,
  setSelectedMonths,
  title,
  size = 'medium',
  layout = 'horizontal',
  stacks,
  justify = 'center'
}) => {
  // Month abbreviations
  const monthLabels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

  // Convert month numbers (1-12) to 0-based indices (0-11)
  const selectedIndices = selectedMonths.map(month => month - 1);

  // Convert 0-based indices back to month numbers (1-12)
  const handleSetSelected = (indices) => {
    const months = indices.map(index => index + 1).sort((a, b) => a - b);
    setSelectedMonths(months);
  };

  return (
    <CheckBoxPicker
      labels={monthLabels}
      selected={selectedIndices}
      setSelected={handleSetSelected}
      title={title}
      size={size}
      layout={layout}
      stacks={stacks}
      justify={justify}
    />
  );
};

MonthPicker.propTypes = {
  selectedMonths: PropTypes.arrayOf(PropTypes.number).isRequired,
  setSelectedMonths: PropTypes.func.isRequired,
  title: PropTypes.string,
  size: PropTypes.oneOf(['small', 'medium', 'large']),
  layout: PropTypes.oneOf(['horizontal', 'vertical']),
  stacks: PropTypes.number.isRequired,
  justify: PropTypes.oneOf(['left', 'right', 'center', 'top', 'bottom'])
};

export default MonthPicker;
