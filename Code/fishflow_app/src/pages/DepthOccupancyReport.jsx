import React, { useState, useEffect, useMemo } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import TitleBar from '../components/common/TitleBar';
import MonthPicker from '../components/common/MonthPicker';
import HourPicker from '../components/common/HourPicker';
import CellMap from '../components/mapping/CellMap';
import ContourDateGraph from '../components/plotting/ContourDateGraph';
import {
  loadGlobalData,
  loadOccupancy,
  filterByMonth,
  buildHighlightIndices,
  calculateFilteredMinimums,
  parseUrlParams,
  updateUrlParams,
  debounce
} from './depthOccupancyHelpers';
import './DepthOccupancyReport.css';

/**
 * LoadingSpinner - Simple loading spinner component.
 */
const LoadingSpinner = ({ size = 'medium' }) => {
  const sizeMap = { small: '30px', medium: '50px', large: '70px' };
  return (
    <div className="loading-spinner" style={{ width: sizeMap[size], height: sizeMap[size] }}>
      <div className="spinner"></div>
    </div>
  );
};

/**
 * ErrorDisplay - Error message with retry button.
 */
const ErrorDisplay = ({ error, onRetry }) => {
  return (
    <div className="error-display">
      <div className="error-message">{error}</div>
      <button className="error-retry-button" onClick={onRetry}>
        Retry
      </button>
    </div>
  );
};

/**
 * DepthOccupancyReport - Main page for depth occupancy visualization.
 *
 * Displays an interactive map with depth occupancy predictions and allows
 * users to filter by months/hours and drill down into specific cells.
 */
const DepthOccupancyReport = () => {
  const { scenario_id } = useParams();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  // Default selections
  const DEFAULT_MONTHS = [1, 2, 3, 4];
  const DEFAULT_HOURS = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18];

  // State for global data
  const [scenario, setScenario] = useState(null);
  const [geometries, setGeometries] = useState(null);
  const [cell_depths, setCellDepths] = useState(null);
  const [timestamps, setTimestamps] = useState(null);
  const [minimums, setMinimums] = useState(null);

  // State for occupancy data (loaded per cell)
  const [occupancy_data, setOccupancyData] = useState({});

  // State for user selections
  const [selectedMonths, setSelectedMonths] = useState(DEFAULT_MONTHS);
  const [selectedHours, setSelectedHours] = useState(DEFAULT_HOURS);
  const [selectedCells, setSelectedCells] = useState([]);

  // Derived state
  const [filtered_timestamps, setFilteredTimestamps] = useState([]);
  const [filtered_occupancy_data, setFilteredOccupancyData] = useState({});
  const [filtered_minimums, setFilteredMinimums] = useState({});
  const [highlight_indices, setHighlightIndices] = useState([]);

  // Loading and error states
  const [isLoadingGlobal, setIsLoadingGlobal] = useState(true);
  const [isLoadingOccupancy, setIsLoadingOccupancy] = useState(false);
  const [loadError, setLoadError] = useState(null);

  // Create debounced URL update function (300ms delay)
  const debouncedUpdateUrlParams = useMemo(
    () => debounce(updateUrlParams, 300),
    []
  );

  // Load global data on mount
  useEffect(() => {
    const loadData = async () => {
      setIsLoadingGlobal(true);
      setLoadError(null);

      try {
        const data = await loadGlobalData(scenario_id);
        setScenario(data.scenario);
        setGeometries(data.geometries);
        setCellDepths(data.cell_depths);
        setTimestamps(data.timestamps);
        setMinimums(data.minimums);

        // Parse URL params or use defaults
        const urlParams = parseUrlParams(searchParams);
        const months = urlParams.months || DEFAULT_MONTHS;
        const hours = urlParams.hours || DEFAULT_HOURS;

        // Determine default cell
        let defaultCell = null;
        if (data.geometries && data.geometries.features && data.geometries.features.length > 0) {
          defaultCell = String(data.geometries.features[0].properties.cell_id);
        }
        const cell = urlParams.cell_id || defaultCell;

        setSelectedMonths(months);
        setSelectedHours(hours);
        if (cell) {
          setSelectedCells([cell]);
        }

        setIsLoadingGlobal(false);
      } catch (error) {
        setLoadError(`Failed to load scenario ${scenario_id}. Error: ${error.message}`);
        setIsLoadingGlobal(false);
      }
    };

    loadData();
  }, [scenario_id, searchParams]);

  // Update filtered minimums when selections change
  useEffect(() => {
    if (minimums && cell_depths) {
      const newFilteredMinimums = calculateFilteredMinimums(
        minimums,
        cell_depths,
        selectedMonths,
        selectedHours
      );
      setFilteredMinimums(newFilteredMinimums);
    }
  }, [minimums, cell_depths, selectedMonths, selectedHours]);

  // Update filtered timestamps and occupancy when months change
  useEffect(() => {
    if (timestamps && Object.keys(occupancy_data).length > 0) {
      const { filtered_timestamps: newFiltered, filtered_occupancy_data: newFilteredOccupancy } =
        filterByMonth(timestamps, selectedMonths, occupancy_data);
      setFilteredTimestamps(newFiltered);
      setFilteredOccupancyData(newFilteredOccupancy);
    }
  }, [timestamps, selectedMonths, occupancy_data]);

  // Update highlight indices when hours or filtered timestamps change
  useEffect(() => {
    if (filtered_timestamps.length > 0) {
      const newHighlightIndices = buildHighlightIndices(filtered_timestamps, selectedHours);
      setHighlightIndices(newHighlightIndices);
    }
  }, [filtered_timestamps, selectedHours]);

  // Load occupancy data when cell selection changes
  useEffect(() => {
    const loadCellData = async () => {
      if (selectedCells.length > 0 && cell_depths && !occupancy_data[selectedCells[0]]) {
        setIsLoadingOccupancy(true);
        setLoadError(null);

        try {
          const newOccupancyData = { ...occupancy_data };
          await loadOccupancy(scenario_id, selectedCells[0], cell_depths, newOccupancyData);
          setOccupancyData(newOccupancyData);
          setIsLoadingOccupancy(false);
        } catch (error) {
          setLoadError(`Failed to load occupancy for cell ${selectedCells[0]}. Error: ${error.message}`);
          setIsLoadingOccupancy(false);
        }
      }
    };

    loadCellData();
  }, [selectedCells, cell_depths, scenario_id, occupancy_data]);

  // Update URL when selections change (debounced to avoid excessive updates)
  useEffect(() => {
    if (selectedCells.length > 0 && !isLoadingGlobal) {
      debouncedUpdateUrlParams(scenario_id, selectedMonths, selectedHours, selectedCells[0]);
    }
  }, [selectedMonths, selectedHours, selectedCells, scenario_id, isLoadingGlobal, debouncedUpdateUrlParams]);

  // Navigation handlers
  const handleBack = () => navigate('/depth_occupancy/example');
  const handleHome = () => navigate('/depth_occupancy/example');

  // Retry handler
  const handleRetry = () => {
    window.location.reload();
  };

  // Show loading spinner during initial load
  if (isLoadingGlobal) {
    return (
      <div className="depth-occupancy-report depth-occupancy-report--loading">
        <LoadingSpinner size="medium" />
      </div>
    );
  }

  // Show error if global load failed
  if (loadError && !scenario) {
    return (
      <div className="depth-occupancy-report depth-occupancy-report--loading">
        <ErrorDisplay error={loadError} onRetry={handleRetry} />
      </div>
    );
  }

  return (
    <div className="depth-occupancy-report">
      <div className="depth-occupancy-report__title-bar">
        <TitleBar
          scenarioName={scenario?.name || 'Loading...'}
          reportType="Depth Occupancy Report"
          onBack={handleBack}
          onHome={handleHome}
        />
      </div>

      <div className="depth-occupancy-report__hour-picker">
        <HourPicker
          selectedHours={selectedHours}
          setSelectedHours={setSelectedHours}
          title="Potential Net Set Hours"
          size="medium"
          layout="horizontal"
          stacks={2}
          justify="left"
        />
      </div>

      <div className="depth-occupancy-report__month-picker">
        <MonthPicker
          selectedMonths={selectedMonths}
          setSelectedMonths={setSelectedMonths}
          title="Potential Harvest Months"
          size="medium"
          layout="vertical"
          stacks={2}
          justify="top"
        />
      </div>

      <div className="depth-occupancy-report__cell-map">
        {geometries && (
          <CellMap
            allowMultiSelect={false}
            values={filtered_minimums}
            geojson={geometries}
            unit="Minimum Likelihood of Occupancy"
            lowColor="#e8f4f8"
            highColor="#1589b0"
            selectedCells={selectedCells}
            setSelectedCells={setSelectedCells}
            center={scenario?.center || [0, 0]}
            zoom={scenario?.zoom || 5}
            geometries={geometries}
            legend_size="medium"
            legend_layout="vertical"
            legend_background="#ffffff"
          />
        )}
      </div>

      <div className="depth-occupancy-report__contour-date-graph">
        {isLoadingOccupancy ? (
          <div className="graph-loading">
            <LoadingSpinner size="small" />
          </div>
        ) : loadError && selectedCells.length > 0 && !occupancy_data[selectedCells[0]] ? (
          <div className="graph-loading">
            <ErrorDisplay error={loadError} onRetry={handleRetry} />
          </div>
        ) : selectedCells.length > 0 && filtered_occupancy_data[selectedCells[0]] ? (
          <ContourDateGraph
            complete_y={filtered_occupancy_data[selectedCells[0]]}
            complete_x={filtered_timestamps}
            highlight_indices={highlight_indices}
            support={scenario?.support || []}
            x_label="Datetime"
            y_label="Likelihood of Occupancy"
            title="Likelihood of Occupancy"
            size="medium"
          />
        ) : (
          <div className="graph-placeholder">Select a cell to view occupancy data</div>
        )}
      </div>
    </div>
  );
};

export default DepthOccupancyReport;
