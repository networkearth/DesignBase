import React from 'react';
import CheckBoxPicker from './CheckBoxPicker';

/**
 * HourPicker - Specialized wrapper around CheckBoxPicker for hour selection.
 *
 * Provides a convenient interface for selecting hours (0-23) while internally
 * managing the conversion to 0-based indices for CheckBoxPicker.
 *
 * @param {Object} props
 * @param {number[]} props.selectedHours - Array of selected hour numbers (0-23), sorted ascending
 * @param {Function} props.setSelectedHours - Setter function for selectedHours
 * @param {string} [props.title] - Title text displayed above the hour picker
 * @param {"small"|"medium"|"large"} [props.size="medium"] - Controls text and box sizing
 * @param {"horizontal"|"vertical"} [props.layout="horizontal"] - Primary direction of arrangement
 * @param {number} props.stacks - Number of rows (horizontal) or columns (vertical)
 * @param {"left"|"right"|"center"|"top"|"bottom"} [props.justify="center"] - Alignment within container
 * @returns {JSX.Element}
 *
 * @example
 * <HourPicker
 *   selectedHours={[6, 7, 8, 9, 10, 11, 12]}
 *   setSelectedHours={setSelectedHours}
 *   title="Select Hours"
 *   size="medium"
 *   layout="horizontal"
 *   stacks={4}
 *   justify="center"
 * />
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
  // Create labels for all 24 hours (0-23)
  const labels = Array.from({ length: 24 }, (_, i) => String(i));

  // Hours (0-23) map directly to 0-based indices (0-23)
  // So selected hours are the same as selected indices
  const selected = selectedHours;

  // Pass through directly - no conversion needed
  const setSelected = setSelectedHours;

  return (
    <CheckBoxPicker
      labels={labels}
      selected={selected}
      setSelected={setSelected}
      title={title}
      size={size}
      layout={layout}
      stacks={stacks}
      justify={justify}
    />
  );
};

export default HourPicker;
