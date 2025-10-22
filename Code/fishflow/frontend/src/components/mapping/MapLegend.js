import React from 'react';
import PropTypes from 'prop-types';

/**
 * MapLegend - A static display component for map visualizations
 * Displays color swatches paired with their corresponding labels
 */
const MapLegend = ({
  colorScale,
  unit,
  size = 'medium',
  layout = 'vertical',
  background = '#ffffff'
}) => {
  // Size-based styling configurations
  const sizeConfig = {
    'x-small': {
      fontSize: '0.75rem',
      padding: '0.375rem',
      swatchSize: '0.75rem',
      gap: '0.25rem'
    },
    'small': {
      fontSize: '0.875rem',
      padding: '0.5rem',
      swatchSize: '1rem',
      gap: '0.25rem'
    },
    'medium': {
      fontSize: '1rem',
      padding: '0.75rem',
      swatchSize: '1.25rem',
      gap: '0.5rem'
    },
    'large': {
      fontSize: '1.25rem',
      padding: '1rem',
      swatchSize: '1.5rem',
      gap: '0.5rem'
    }
  };

  const config = sizeConfig[size];

  const containerStyle = {
    backgroundColor: background,
    border: '1px solid #dee2e6',
    borderRadius: '0.25rem',
    padding: config.padding,
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    fontSize: config.fontSize,
    color: '#212529'
  };

  const titleStyle = {
    fontWeight: '500',
    marginBottom: layout === 'vertical' ? '0.5rem' : '0',
    marginRight: layout === 'horizontal' ? '0.5rem' : '0'
  };

  const itemsContainerStyle = {
    display: 'flex',
    flexDirection: layout === 'vertical' ? 'column' : 'row',
    gap: config.gap,
    alignItems: layout === 'horizontal' ? 'center' : 'stretch'
  };

  const itemStyle = {
    display: 'flex',
    flexDirection: layout === 'vertical' ? 'row' : 'column',
    alignItems: 'center',
    gap: '0.5rem'
  };

  const swatchStyle = (color) => ({
    width: config.swatchSize,
    height: config.swatchSize,
    backgroundColor: color,
    border: '1px solid #dee2e6',
    flexShrink: 0
  });

  const labelStyle = {
    fontWeight: '400'
  };

  return (
    <div style={containerStyle} role="img" aria-label={`Map legend for ${unit}`}>
      <div style={titleStyle}>{unit}</div>
      <div style={itemsContainerStyle}>
        {colorScale.map(([label, color], index) => (
          <div key={index} style={itemStyle}>
            <div style={swatchStyle(color)} />
            <span style={labelStyle}>{label}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

MapLegend.propTypes = {
  colorScale: PropTypes.arrayOf(
    PropTypes.arrayOf(PropTypes.string)
  ).isRequired,
  unit: PropTypes.string.isRequired,
  size: PropTypes.oneOf(['x-small', 'small', 'medium', 'large']),
  layout: PropTypes.oneOf(['vertical', 'horizontal']),
  background: PropTypes.string
};

export default MapLegend;
