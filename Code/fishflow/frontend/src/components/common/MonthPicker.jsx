import React from 'react';
import CheckBoxPicker from './CheckBoxPicker';

/**
 * MonthPicker Component
 *
 * A specialized wrapper around CheckBoxPicker configured for month selection.
 * Converts between 1-based month numbers (1-12) and 0-based indices (0-11).
 *
 * @param {number[]} selectedMonths - Array of selected month numbers (1-12), sorted ascending
 * @param {Function} setSelectedMonths - Setter function for selectedMonths
 * @param {string} title - Title text displayed above the month selector
 * @param {string} size - "small" | "medium" | "large"
 * @param {string} layout - "horizontal" | "vertical"
 * @param {number} stacks - Number of rows (horizontal) or columns (vertical)
 * @param {string} justify - "left" | "right" | "center" (horizontal) or "top" | "bottom" | "center" (vertical)
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
  const monthLabels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

  // Convert month numbers (1-12) to 0-based indices (0-11)
  const selectedIndices = selectedMonths.map(month => month - 1);

  // Convert 0-based indices back to month numbers (1-12)
  const handleSetSelected = (indices) => {
    const months = indices.map(index => index + 1);
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

export default MonthPicker;
