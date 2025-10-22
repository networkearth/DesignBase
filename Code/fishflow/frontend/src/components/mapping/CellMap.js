import React, { useState, useEffect, useRef } from 'react';
import PropTypes from 'prop-types';
import { MapContainer, TileLayer, GeoJSON, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import MapLegend from './MapLegend';
import { interpolateColor, buildColorScale } from '../../functions/common/coloring';

/**
 * Component to handle map re-centering when geometries change
 */
const MapController = ({ center, zoom, geometries }) => {
  const map = useMap();
  const prevGeometriesRef = useRef();

  useEffect(() => {
    // Only recenter if geometries actually changed
    if (prevGeometriesRef.current !== geometries) {
      map.setView(center, zoom);
      prevGeometriesRef.current = geometries;
    }
  }, [geometries, center, zoom, map]);

  return null;
};

/**
 * CellMap - Interactive map component displaying colored polygons based on values
 * Supports cell selection and displays a color legend
 */
const CellMap = ({
  allowMultiSelect = false,
  values,
  geojson,
  unit,
  lowColor,
  highColor,
  selectedCells,
  setSelectedCells,
  center,
  zoom,
  legend_size = 'medium',
  legend_layout = 'vertical',
  legend_background = '#ffffff'
}) => {
  const [colors, setColors] = useState({});
  const [colorScale, setColorScale] = useState([]);
  const [hoveredCell, setHoveredCell] = useState(null);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  // Calculate colors and color scale when values or colors change
  useEffect(() => {
    const cellIds = Object.keys(values);
    const cellValues = cellIds.map(id => values[id]);

    // Interpolate colors
    const interpolatedColors = interpolateColor(lowColor, highColor, cellValues);

    // Create colors object mapping cell_id to color
    const colorsMap = {};
    cellIds.forEach((id, index) => {
      colorsMap[id] = interpolatedColors[index];
    });
    setColors(colorsMap);

    // Build color scale using quantiles
    const quantiles = [0, 25, 50, 75, 100];
    const scale = buildColorScale(quantiles, cellValues, interpolatedColors);
    setColorScale(scale);
  }, [values, lowColor, highColor]);

  // Handle cell click
  const handleCellClick = (cellId) => {
    if (allowMultiSelect) {
      // Multi-select mode
      if (selectedCells.includes(cellId)) {
        // Deselect cell
        setSelectedCells(selectedCells.filter(id => id !== cellId));
      } else {
        // Add to selection
        setSelectedCells([...selectedCells, cellId]);
      }
    } else {
      // Single-select mode
      if (selectedCells.includes(cellId)) {
        // Deselect if already selected
        setSelectedCells([]);
      } else {
        // Replace selection with new cell
        setSelectedCells([cellId]);
      }
    }
  };

  // Handle mouse movement for tooltip
  const handleMouseMove = (e) => {
    setMousePosition({ x: e.clientX, y: e.clientY });
  };

  // Clear all selections
  const handleClearSelection = () => {
    setSelectedCells([]);
  };

  // Style function for GeoJSON features
  const getFeatureStyle = (feature) => {
    const cellId = feature.properties.cell_id;
    const isSelected = selectedCells.includes(cellId);
    const color = colors[cellId];

    return {
      fillColor: color || 'transparent',
      fillOpacity: color ? 0.7 : 0,
      color: isSelected ? '#212529' : '#dee2e6',
      weight: isSelected ? 3 : 1,
      transition: 'all 0.15s ease-in-out'
    };
  };

  // Event handlers for each feature
  const onEachFeature = (feature, layer) => {
    const cellId = feature.properties.cell_id;

    layer.on({
      click: () => handleCellClick(cellId),
      mouseover: (e) => {
        setHoveredCell({ cellId, value: values[cellId] });
        layer.setStyle({
          weight: 2
        });
      },
      mouseout: () => {
        setHoveredCell(null);
        layer.setStyle({
          weight: selectedCells.includes(cellId) ? 3 : 1
        });
      }
    });
  };

  const containerStyle = {
    width: '100%',
    height: '100%',
    position: 'relative',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
  };

  const legendContainerStyle = {
    position: 'absolute',
    top: '1rem',
    right: '1rem',
    zIndex: 1000
  };

  const clearButtonStyle = {
    position: 'absolute',
    bottom: '1rem',
    right: '1rem',
    zIndex: 1000,
    backgroundColor: legend_background,
    border: '1px solid #dee2e6',
    borderRadius: '0.25rem',
    padding: '0.5rem 1rem',
    fontSize: '0.875rem',
    color: '#212529',
    cursor: 'pointer',
    transition: 'all 0.15s ease-in-out'
  };

  const clearButtonHoverStyle = {
    ...clearButtonStyle,
    backgroundColor: 'rgba(13, 110, 253, 0.1)'
  };

  const tooltipStyle = {
    position: 'fixed',
    left: `${mousePosition.x + 10}px`,
    top: `${mousePosition.y + 10}px`,
    backgroundColor: '#212529',
    color: '#ffffff',
    fontSize: '0.875rem',
    padding: '0.5rem',
    borderRadius: '0.25rem',
    pointerEvents: 'none',
    zIndex: 10000,
    whiteSpace: 'nowrap'
  };

  const [isHoveringButton, setIsHoveringButton] = useState(false);

  return (
    <div style={containerStyle} onMouseMove={handleMouseMove}>
      <MapContainer
        center={center}
        zoom={zoom}
        style={{ width: '100%', height: '100%' }}
        zoomControl={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <GeoJSON
          data={geojson}
          style={getFeatureStyle}
          onEachFeature={onEachFeature}
          key={JSON.stringify(geojson)}
        />
        <MapController center={center} zoom={zoom} geometries={geojson} />
      </MapContainer>

      {/* Map Legend */}
      <div style={legendContainerStyle}>
        <MapLegend
          colorScale={colorScale}
          unit={unit}
          size={legend_size}
          layout={legend_layout}
          background={legend_background}
        />
      </div>

      {/* Clear Selection Button */}
      {allowMultiSelect && selectedCells.length > 0 && (
        <button
          style={isHoveringButton ? clearButtonHoverStyle : clearButtonStyle}
          onClick={handleClearSelection}
          onMouseEnter={() => setIsHoveringButton(true)}
          onMouseLeave={() => setIsHoveringButton(false)}
          aria-label="Clear selection"
        >
          Clear Selection
        </button>
      )}

      {/* Tooltip */}
      {hoveredCell && hoveredCell.value != null && (
        <div style={tooltipStyle}>
          {hoveredCell.value} {unit}
        </div>
      )}
    </div>
  );
};

CellMap.propTypes = {
  allowMultiSelect: PropTypes.bool,
  values: PropTypes.objectOf(PropTypes.number).isRequired,
  geojson: PropTypes.object.isRequired,
  unit: PropTypes.string.isRequired,
  lowColor: PropTypes.string.isRequired,
  highColor: PropTypes.string.isRequired,
  selectedCells: PropTypes.arrayOf(PropTypes.string).isRequired,
  setSelectedCells: PropTypes.func.isRequired,
  center: PropTypes.arrayOf(PropTypes.number).isRequired,
  zoom: PropTypes.number.isRequired,
  legend_size: PropTypes.oneOf(['x-small', 'small', 'medium', 'large']),
  legend_layout: PropTypes.oneOf(['vertical', 'horizontal']),
  legend_background: PropTypes.string
};

export default CellMap;
