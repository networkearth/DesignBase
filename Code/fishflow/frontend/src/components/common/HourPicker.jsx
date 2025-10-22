import React from 'react';
import PropTypes from 'prop-types';
import CheckBoxPicker from './CheckBoxPicker';

const HourPicker = ({
  selectedHours,
  setSelectedHours,
  title,
  size = 'medium',
  layout = 'horizontal',
  stacks,
  justify = 'center'
}) => {
  // Generate labels for hours 0-23
  const hourLabels = Array.from({ length: 24 }, (_, i) => i.toString());

  // Hours (0-23) map directly to indices (0-23), so no conversion needed
  const handleSetSelected = (indices) => {
    setSelectedHours(indices);
  };

  return (
    <CheckBoxPicker
      labels={hourLabels}
      selected={selectedHours}
      setSelected={handleSetSelected}
      title={title}
      size={size}
      layout={layout}
      stacks={stacks}
      justify={justify}
    />
  );
};

HourPicker.propTypes = {
  selectedHours: PropTypes.arrayOf(PropTypes.number).isRequired,
  setSelectedHours: PropTypes.func.isRequired,
  title: PropTypes.string,
  size: PropTypes.oneOf(['small', 'medium', 'large']),
  layout: PropTypes.oneOf(['horizontal', 'vertical']),
  stacks: PropTypes.number.isRequired,
  justify: PropTypes.oneOf(['left', 'right', 'center', 'top', 'bottom'])
};

export default HourPicker;
