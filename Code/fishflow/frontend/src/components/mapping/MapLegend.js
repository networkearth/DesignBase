import React from 'react';
import './MapLegend.css';

/**
 * MapLegend Component
 *
 * A static display component providing a legend for map visualizations
 * by showing color swatches paired with their corresponding labels.
 *
 * @param {Array<[string, string]>} colorScale - Array of [label, color] tuples
 * @param {string} unit - Name of the unit being displayed (shown as title)
 * @param {string} size - "x-small" | "small" | "medium" | "large" - Controls sizing
 * @param {string} layout - "vertical" | "horizontal" - Arrangement of swatches and labels
 * @param {string} background - Hex color code for component background
 */
const MapLegend = ({
  colorScale,
  unit,
  size = 'medium',
  layout = 'vertical',
  background = '#ffffff'
}) => {
  const containerClass = `map-legend map-legend--${size} map-legend--${layout}`;

  return (
    <div
      className={containerClass}
      style={{ backgroundColor: background }}
      aria-label="Map legend"
    >
      <div className="map-legend__title">{unit}</div>
      <div className="map-legend__items">
        {colorScale.map(([label, color], index) => (
          <div key={index} className="map-legend__item">
            <div
              className="map-legend__swatch"
              style={{ backgroundColor: color }}
              aria-hidden="true"
            />
            <div className="map-legend__label">{label}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MapLegend;
