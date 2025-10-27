import React from 'react';
import './CheckBoxPicker.css';

/**
 * CheckBoxPicker Component
 *
 * A customizable checkbox grid for selecting multiple items from a list.
 *
 * @param {string[]} labels - Array of strings to display in each box
 * @param {number[]} selected - Array of selected indices (0-based), sorted ascending
 * @param {Function} setSelected - Setter function for selected state
 * @param {string} title - Title text displayed above the picker (optional)
 * @param {string} size - "small" | "medium" | "large" - Controls text and box sizing
 * @param {string} layout - "horizontal" | "vertical" - Primary direction of arrangement
 * @param {number} stacks - Number of rows (horizontal) or columns (vertical)
 * @param {string} justify - Alignment/distribution of boxes within container
 */
const CheckBoxPicker = ({
  labels,
  selected = [],
  setSelected,
  title,
  size = 'medium',
  layout = 'horizontal',
  stacks,
  justify = 'center'
}) => {
  const handleClick = (index) => {
    if (selected.includes(index)) {
      // Remove from selection
      setSelected(selected.filter(i => i !== index).sort((a, b) => a - b));
    } else {
      // Add to selection
      setSelected([...selected, index].sort((a, b) => a - b));
    }
  };

  const handleKeyPress = (event, index) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      handleClick(index);
    }
  };

  const containerClass = `checkbox-picker checkbox-picker--${size} checkbox-picker--${layout} checkbox-picker--justify-${justify}`;
  const gridClass = `checkbox-picker__grid checkbox-picker__grid--${layout} checkbox-picker__grid--stacks-${stacks}`;

  return (
    <div className={containerClass} role="group" aria-label={title || 'Checkbox picker'}>
      {title && <div className="checkbox-picker__title">{title}</div>}
      <div className={gridClass}>
        {labels.map((label, index) => (
          <div
            key={index}
            className={`checkbox-picker__box ${selected.includes(index) ? 'checkbox-picker__box--selected' : ''}`}
            onClick={() => handleClick(index)}
            onKeyPress={(e) => handleKeyPress(e, index)}
            role="checkbox"
            aria-checked={selected.includes(index)}
            tabIndex={0}
          >
            {label}
          </div>
        ))}
      </div>
    </div>
  );
};

export default CheckBoxPicker;
