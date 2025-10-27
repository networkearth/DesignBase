import React, { useEffect, useRef, useState } from 'react';
import { MapContainer, TileLayer, GeoJSON, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import MapLegend from './MapLegend';
import { interpolateColor, buildColorScale } from '../../functions/common/coloring';
import './CellMap.css';

/**
 * Component to recenter the map when geometries change
 */
function RecenterMap({ center, zoom, triggerRecenter }) {
  const map = useMap();

  useEffect(() => {
    if (triggerRecenter && center && zoom) {
      map.setView(center, zoom);
    }
  }, [triggerRecenter, center, zoom, map]);

  return null;
}

/**
 * CellMap Component
 *
 * Displays polygons on a map colored by values and allows user to select cells.
 *
 * @param {boolean} allowMultiSelect - Whether multiple cell selection is allowed
 * @param {Object} values - Object mapping cell_id to numeric value (nulls allowed)
 * @param {Object} geojson - GeoJSON of polygons with cell_id for each polygon
 * @param {string} unit - Unit of measurement for values
 * @param {string} lowColor - Hex color for minimum value
 * @param {string} highColor - Hex color for maximum value
 * @param {string[]} selectedCells - Array of selected cell_id strings
 * @param {Function} setSelectedCells - Setter function for selectedCells
 * @param {[number, number]} center - Array [latitude, longitude] for map center
 * @param {number} zoom - Initial zoom level
 * @param {string} legend_size - Size for MapLegend
 * @param {string} legend_layout - Layout for MapLegend
 * @param {string} legend_background - Background color for MapLegend
 */
const CellMap = ({
  allowMultiSelect,
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
  const [hoveredCell, setHoveredCell] = useState(null);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [recenterTrigger, setRecenterTrigger] = useState(0);
  const prevGeojsonRef = useRef(null);

  // Detect when geojson changes to trigger recenter
  useEffect(() => {
    if (geojson !== prevGeojsonRef.current) {
      prevGeojsonRef.current = geojson;
      setRecenterTrigger(prev => prev + 1);
    }
  }, [geojson]);

  // Extract values array for color interpolation
  const valuesList = Object.values(values);
  const cellIds = Object.keys(values);

  // Interpolate colors
  const colorsList = interpolateColor(lowColor, highColor, valuesList);

  // Create colors object mapping cell_id to color
  const colors = {};
  cellIds.forEach((cellId, index) => {
    colors[cellId] = colorsList[index];
  });

  // Build color scale for legend (quantiles: 0, 25, 50, 75, 100)
  const colorScale = buildColorScale([0, 25, 50, 75, 100], valuesList, colorsList);

  // Handle cell click
  const handleCellClick = (cellId) => {
    if (allowMultiSelect) {
      if (selectedCells.includes(cellId)) {
        // Deselect
        setSelectedCells(selectedCells.filter(id => id !== cellId));
      } else {
        // Add to selection
        setSelectedCells([...selectedCells, cellId]);
      }
    } else {
      if (selectedCells.includes(cellId)) {
        // Deselect
        setSelectedCells([]);
      } else {
        // Replace selection
        setSelectedCells([cellId]);
      }
    }
  };

  // Handle clear selection
  const handleClearSelection = () => {
    setSelectedCells([]);
  };

  // Style each feature
  const styleFeature = (feature) => {
    const cellId = feature.properties.cell_id?.toString();
    const color = colors[cellId];
    const isSelected = selectedCells.includes(cellId);

    return {
      fillColor: color || 'transparent',
      fillOpacity: color ? 0.7 : 0,
      color: isSelected ? '#212529' : '#dee2e6',
      weight: isSelected ? 3 : 1
    };
  };

  // Handle feature events
  const onEachFeature = (feature, layer) => {
    const cellId = feature.properties.cell_id?.toString();

    layer.on({
      click: () => handleCellClick(cellId),
      mouseover: (e) => {
        setHoveredCell({ cellId, value: values[cellId] });
        layer.setStyle({
          weight: selectedCells.includes(cellId) ? 3 : 2
        });
      },
      mouseout: () => {
        setHoveredCell(null);
        layer.setStyle({
          weight: selectedCells.includes(cellId) ? 3 : 1
        });
      },
      mousemove: (e) => {
        setMousePosition({ x: e.originalEvent.clientX, y: e.originalEvent.clientY });
      }
    });
  };

  return (
    <div className="cell-map">
      <MapContainer
        center={center}
        zoom={zoom}
        style={{ width: '100%', height: '100%' }}
        scrollWheelZoom={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {geojson && (
          <GeoJSON
            key={recenterTrigger}
            data={geojson}
            style={styleFeature}
            onEachFeature={onEachFeature}
          />
        )}
        <RecenterMap center={center} zoom={zoom} triggerRecenter={recenterTrigger} />
      </MapContainer>

      {/* Legend */}
      <div className="cell-map__legend">
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
          className="cell-map__clear-button"
          style={{ backgroundColor: legend_background }}
          onClick={handleClearSelection}
        >
          Clear Selection
        </button>
      )}

      {/* Tooltip */}
      {hoveredCell && hoveredCell.value !== null && hoveredCell.value !== undefined && (
        <div
          className="cell-map__tooltip"
          style={{
            left: `${mousePosition.x + 10}px`,
            top: `${mousePosition.y + 10}px`
          }}
        >
          {hoveredCell.value.toFixed(3)} {unit}
        </div>
      )}
    </div>
  );
};

export default CellMap;
