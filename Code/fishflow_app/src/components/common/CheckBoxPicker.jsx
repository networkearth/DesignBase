import React from 'react';
import './CheckBoxPicker.css';

/**
 * CheckBoxPicker - A customizable multi-select checkbox component.
 *
 * Displays a grid of selectable boxes with customizable layout, sizing, and styling.
 * Users can toggle selections by clicking boxes.
 *
 * @param {Object} props
 * @param {string[]} props.labels - Array of strings to display in each box
 * @param {number[]} props.selected - Array of selected indices (0-based), sorted ascending
 * @param {Function} props.setSelected - Setter function for selected state
 * @param {string} [props.title] - Title text displayed above the picker
 * @param {"small"|"medium"|"large"} [props.size="medium"] - Controls text and box sizing
 * @param {"horizontal"|"vertical"} [props.layout="horizontal"] - Primary direction of arrangement
 * @param {number} props.stacks - Number of rows (horizontal) or columns (vertical)
 * @param {"left"|"right"|"center"|"top"|"bottom"} [props.justify="center"] - Alignment within container
 * @returns {JSX.Element}
 *
 * @example
 * <CheckBoxPicker
 *   labels={['Jan', 'Feb', 'Mar']}
 *   selected={[0, 2]}
 *   setSelected={setSelected}
 *   title="Select Months"
 *   size="medium"
 *   layout="horizontal"
 *   stacks={3}
 *   justify="center"
 * />
 */
const CheckBoxPicker = ({
  labels,
  selected,
  setSelected,
  title,
  size = 'medium',
  layout = 'horizontal',
  stacks,
  justify = 'center'
}) => {
  /**
   * Handles box click events, toggling selection state.
   *
   * @param {number} index - Index of the clicked box
   */
  const handleClick = (index) => {
    if (selected.includes(index)) {
      // Remove from selection
      setSelected(selected.filter(i => i !== index).sort((a, b) => a - b));
    } else {
      // Add to selection
      setSelected([...selected, index].sort((a, b) => a - b));
    }
  };

  /**
   * Handles keyboard navigation and selection.
   *
   * @param {KeyboardEvent} event - Keyboard event
   * @param {number} index - Index of the focused box
   */
  const handleKeyDown = (event, index) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      handleClick(index);
    }
  };

  // Determine CSS class names based on props
  const containerClass = `checkbox-picker checkbox-picker--${size} checkbox-picker--${layout}`;
  const gridClass = `checkbox-picker__grid checkbox-picker__grid--${layout} checkbox-picker__grid--${justify}`;
  const gridStyle = {
    gridTemplateRows: layout === 'horizontal' ? `repeat(${stacks}, 1fr)` : undefined,
    gridTemplateColumns: layout === 'vertical' ? `repeat(${stacks}, 1fr)` : undefined
  };

  return (
    <div className={containerClass} role="group" aria-label={title || 'Checkbox picker'}>
      {title && <div className="checkbox-picker__title">{title}</div>}
      <div className={gridClass} style={gridStyle}>
        {labels.map((label, index) => {
          const isSelected = selected.includes(index);
          const boxClass = `checkbox-picker__box ${isSelected ? 'checkbox-picker__box--selected' : ''}`;

          return (
            <div
              key={index}
              className={boxClass}
              role="checkbox"
              aria-checked={isSelected}
              tabIndex={0}
              onClick={() => handleClick(index)}
              onKeyDown={(e) => handleKeyDown(e, index)}
            >
              {label}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default CheckBoxPicker;
