import React from 'react';
import CheckBoxPicker from './CheckBoxPicker';

/**
 * HourPicker Component
 *
 * A specialized wrapper around CheckBoxPicker configured for hour selection.
 * Hours (0-23) map directly to 0-based indices (0-23), so no conversion needed.
 *
 * @param {number[]} selectedHours - Array of selected hour numbers (0-23), sorted ascending
 * @param {Function} setSelectedHours - Setter function for selectedHours
 * @param {string} title - Title text displayed above the hour picker
 * @param {string} size - "small" | "medium" | "large"
 * @param {string} layout - "horizontal" | "vertical"
 * @param {number} stacks - Number of rows (horizontal) or columns (vertical)
 * @param {string} justify - "left" | "right" | "center" (horizontal) or "top" | "bottom" | "center" (vertical)
 */
const HourPicker = ({
  selectedHours,
  setSelectedHours,
  title,
  size = 'medium',
  layout = 'horizontal',
  stacks,
  justify = 'center'
}) => {
  // Generate hour labels 0-23
  const hourLabels = Array.from({ length: 24 }, (_, i) => i.toString());

  return (
    <CheckBoxPicker
      labels={hourLabels}
      selected={selectedHours}
      setSelected={setSelectedHours}
      title={title}
      size={size}
      layout={layout}
      stacks={stacks}
      justify={justify}
    />
  );
};

export default HourPicker;
