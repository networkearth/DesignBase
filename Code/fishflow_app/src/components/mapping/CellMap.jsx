import React, { useEffect, useState, useRef } from 'react';
import { MapContainer, TileLayer, GeoJSON, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import './CellMap.css';
import MapLegend from './MapLegend';
import { interpolateColor, buildColorScale } from '../../functions/coloring';

/**
 * MapRecenterer - Helper component to recenter map when geometries change.
 */
const MapRecenterer = ({ center, zoom, geometries }) => {
  const map = useMap();
  const prevGeometriesRef = useRef(null);

  useEffect(() => {
    // Only recenter if geometries actually changed
    if (geometries !== prevGeometriesRef.current) {
      map.setView(center, zoom);
      prevGeometriesRef.current = geometries;
    }
  }, [geometries, center, zoom, map]);

  return null;
};

/**
 * CellMap - Interactive map displaying colored polygons with selection.
 *
 * Displays GeoJSON polygons colored by values, allows cell selection,
 * and shows a legend explaining the color scale.
 *
 * @param {Object} props
 * @param {boolean} props.allowMultiSelect - Whether multiple cell selection is allowed
 * @param {Object.<string, number>} props.values - Object mapping cell_id to numeric value
 * @param {Object} props.geojson - GeoJSON FeatureCollection with cell_id for each polygon
 * @param {string} props.unit - Unit of measurement for values
 * @param {string} props.lowColor - Hex color for minimum value
 * @param {string} props.highColor - Hex color for maximum value
 * @param {string[]} props.selectedCells - Array of selected cell_id strings
 * @param {Function} props.setSelectedCells - Setter function for selectedCells
 * @param {[number, number]} props.center - [latitude, longitude] for map center
 * @param {number} props.zoom - Initial zoom level
 * @param {Object} props.geometries - GeoJSON geometries for cells
 * @param {"x-small"|"small"|"medium"|"large"} [props.legend_size="medium"] - Size for MapLegend
 * @param {"vertical"|"horizontal"} [props.legend_layout="vertical"] - Layout for MapLegend
 * @param {string} [props.legend_background="#ffffff"] - Background color for MapLegend
 * @returns {JSX.Element}
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
  geometries,
  legend_size = 'medium',
  legend_layout = 'vertical',
  legend_background = '#ffffff'
}) => {
  // Calculate colors from values
  const colors = interpolateColor(lowColor, highColor, values);

  // Build color scale for legend (using 0, 25, 50, 75, 100 percentiles)
  const colorScale = buildColorScale([0, 25, 50, 75, 100], values, colors);

  // Tooltip state
  const [tooltip, setTooltip] = useState({ visible: false, x: 0, y: 0, content: '' });

  /**
   * Handles cell click for selection/deselection.
   */
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
        // Deselect (allow empty selection)
        setSelectedCells([]);
      } else {
        // Replace selection with single cell
        setSelectedCells([cellId]);
      }
    }
  };

  /**
   * Handles mouse enter on cell - shows tooltip.
   */
  const handleMouseEnter = (e, cellId) => {
    const value = values[cellId];
    if (value !== undefined && value !== null) {
      setTooltip({
        visible: true,
        x: e.originalEvent.clientX,
        y: e.originalEvent.clientY,
        content: `${value.toFixed(3)} ${unit}`
      });
    }
  };

  /**
   * Handles mouse move on cell - updates tooltip position.
   */
  const handleMouseMove = (e) => {
    setTooltip(prev => ({
      ...prev,
      x: e.originalEvent.clientX,
      y: e.originalEvent.clientY
    }));
  };

  /**
   * Handles mouse leave on cell - hides tooltip.
   */
  const handleMouseLeave = () => {
    setTooltip({ visible: false, x: 0, y: 0, content: '' });
  };

  /**
   * Clears all cell selections.
   */
  const handleClearSelection = () => {
    setSelectedCells([]);
  };

  /**
   * Styles each GeoJSON feature (cell).
   */
  const styleFeature = (feature) => {
    const cellId = feature.properties.cell_id;
    const color = colors[cellId] || '#cccccc';
    const isSelected = selectedCells.includes(String(cellId));

    return {
      fillColor: color,
      fillOpacity: 1,
      color: isSelected ? '#212529' : '#dee2e6',
      weight: isSelected ? 3 : 1,
      transition: 'all 0.15s ease-in-out'
    };
  };

  /**
   * Attaches event handlers to each GeoJSON feature.
   */
  const onEachFeature = (feature, layer) => {
    const cellId = String(feature.properties.cell_id);

    layer.on({
      click: () => handleCellClick(cellId),
      mouseover: (e) => handleMouseEnter(e, cellId),
      mousemove: (e) => handleMouseMove(e),
      mouseout: () => handleMouseLeave()
    });
  };

  // Key to force GeoJSON re-render when styles change
  const geoJsonKey = `${selectedCells.join(',')}-${JSON.stringify(colors)}`;

  return (
    <div className="cell-map">
      <MapContainer
        center={center}
        zoom={zoom}
        className="cell-map__container"
        scrollWheelZoom={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <GeoJSON
          key={geoJsonKey}
          data={geojson}
          style={styleFeature}
          onEachFeature={onEachFeature}
        />
        <MapRecenterer center={center} zoom={zoom} geometries={geometries} />
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
          style={{ background: legend_background }}
          onClick={handleClearSelection}
        >
          Clear Selection
        </button>
      )}

      {/* Tooltip */}
      {tooltip.visible && (
        <div
          className="cell-map__tooltip"
          style={{
            left: `${tooltip.x + 10}px`,
            top: `${tooltip.y + 10}px`
          }}
        >
          {tooltip.content}
        </div>
      )}
    </div>
  );
};

export default CellMap;
