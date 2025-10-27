import React from 'react';
import CheckBoxPicker from './CheckBoxPicker';

/**
 * MonthPicker - Specialized wrapper around CheckBoxPicker for month selection.
 *
 * Provides a convenient interface for selecting months (1-12) while internally
 * managing the conversion between 1-based month numbers and 0-based indices.
 *
 * @param {Object} props
 * @param {number[]} props.selectedMonths - Array of selected month numbers (1-12), sorted ascending
 * @param {Function} props.setSelectedMonths - Setter function for selectedMonths
 * @param {string} [props.title] - Title text displayed above the month selector
 * @param {"small"|"medium"|"large"} [props.size="medium"] - Controls text and box sizing
 * @param {"horizontal"|"vertical"} [props.layout="horizontal"] - Primary direction of arrangement
 * @param {number} props.stacks - Number of rows (horizontal) or columns (vertical)
 * @param {"left"|"right"|"center"|"top"|"bottom"} [props.justify="center"] - Alignment within container
 * @returns {JSX.Element}
 *
 * @example
 * <MonthPicker
 *   selectedMonths={[1, 2, 3, 4]}
 *   setSelectedMonths={setSelectedMonths}
 *   title="Select Months"
 *   size="medium"
 *   layout="horizontal"
 *   stacks={3}
 *   justify="center"
 * />
 */
const MonthPicker = ({
  selectedMonths,
  setSelectedMonths,
  title,
  size = 'medium',
  layout = 'horizontal',
  stacks,
  justify = 'center'
}) => {
  // Month abbreviations for display
  const labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

  // Convert month numbers (1-12) to 0-based indices (0-11)
  const selected = selectedMonths.map(month => month - 1);

  // Wrapper to convert 0-based indices back to month numbers (1-12)
  const setSelected = (indices) => {
    const months = indices.map(index => index + 1);
    setSelectedMonths(months);
  };

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

export default MonthPicker;
