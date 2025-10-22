import React from 'react';
import PropTypes from 'prop-types';
import './CheckBoxPicker.css';

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
  const handleBoxClick = (index) => {
    if (selected.includes(index)) {
      // Remove the index and keep sorted order
      setSelected(selected.filter(i => i !== index).sort((a, b) => a - b));
    } else {
      // Add the index and maintain sorted order
      setSelected([...selected, index].sort((a, b) => a - b));
    }
  };

  const handleKeyDown = (e, index) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleBoxClick(index);
    }
  };

  // Calculate grid structure
  const itemsPerStack = Math.ceil(labels.length / stacks);

  // Generate CSS class names
  const containerClass = `checkbox-picker checkbox-picker-${size} checkbox-picker-${layout} checkbox-picker-${justify}`;
  const gridClass = `checkbox-picker-grid checkbox-picker-grid-${layout}`;

  return (
    <div className={containerClass} role="group" aria-label={title || 'Checkbox picker'}>
      {title && <div className="checkbox-picker-title">{title}</div>}
      <div
        className={gridClass}
        style={{
          gridTemplateRows: layout === 'horizontal' ? `repeat(${stacks}, 1fr)` : `repeat(${itemsPerStack}, 1fr)`,
          gridTemplateColumns: layout === 'horizontal' ? `repeat(${itemsPerStack}, 1fr)` : `repeat(${stacks}, 1fr)`
        }}
      >
        {labels.map((label, index) => {
          const isSelected = selected.includes(index);
          return (
            <div
              key={index}
              className={`checkbox-picker-box ${isSelected ? 'selected' : ''}`}
              role="checkbox"
              aria-checked={isSelected}
              tabIndex={0}
              onClick={() => handleBoxClick(index)}
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

CheckBoxPicker.propTypes = {
  labels: PropTypes.arrayOf(PropTypes.string).isRequired,
  selected: PropTypes.arrayOf(PropTypes.number).isRequired,
  setSelected: PropTypes.func.isRequired,
  title: PropTypes.string,
  size: PropTypes.oneOf(['small', 'medium', 'large']),
  layout: PropTypes.oneOf(['horizontal', 'vertical']),
  stacks: PropTypes.number.isRequired,
  justify: PropTypes.oneOf(['left', 'right', 'center', 'top', 'bottom'])
};

export default CheckBoxPicker;
