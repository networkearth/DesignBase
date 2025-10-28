import React from 'react';
import './MapLegend.css';

/**
 * MapLegend - Displays a legend for map visualizations.
 *
 * Shows color swatches paired with labels to help users interpret
 * color-coded map data.
 *
 * @param {Object} props
 * @param {Array.<[string, string]>} props.colorScale - Array of [label, color] tuples
 * @param {string} props.unit - Name of the unit being displayed (shown as title)
 * @param {"x-small"|"small"|"medium"|"large"} [props.size="medium"] - Controls sizing
 * @param {"vertical"|"horizontal"} [props.layout="vertical"] - Arrangement of swatches
 * @param {string} [props.background="#ffffff"] - Background color (hex code)
 * @returns {JSX.Element}
 *
 * @example
 * <MapLegend
 *   colorScale={[
 *     ['0.0', '#e8f4f8'],
 *     ['0.5', '#7fbfd4'],
 *     ['1.0', '#1589b0']
 *   ]}
 *   unit="Occupancy Likelihood"
 *   size="medium"
 *   layout="vertical"
 *   background="#ffffff"
 * />
 */
const MapLegend = ({
  colorScale,
  unit,
  size = 'medium',
  layout = 'vertical',
  background = '#ffffff'
}) => {
  const containerClass = `map-legend map-legend--${size} map-legend--${layout}`;
  const containerStyle = {
    background: background
  };

  return (
    <div
      className={containerClass}
      style={containerStyle}
      role="region"
      aria-label={`Legend for ${unit}`}
    >
      <div className="map-legend__title">{unit}</div>
      <div className="map-legend__items">
        {colorScale.map(([label, color], index) => (
          <div key={index} className="map-legend__item">
            <div
              className="map-legend__swatch"
              style={{ background: color }}
              aria-label={`Color for ${label}`}
            />
            <div className="map-legend__label">{label}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MapLegend;
