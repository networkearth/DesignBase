import React, { useState, useEffect } from 'react';
import { useParams, useSearchParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import TitleBar from '../components/common/TitleBar';
import ErrorPopup from '../components/common/ErrorPopup';
import MonthPicker from '../components/common/MonthPicker';
import HourPicker from '../components/common/HourPicker';
import CellMap from '../components/mapping/CellMap';
import ContourDateGraph from '../components/plotting/ContourDateGraph';
import './DepthOccupancyReport.css';

// Determine API base URL based on environment
const getApiBaseUrl = () => {
  return process.env.REACT_APP_FISHFLOW_MODE === 'dev'
    ? 'http://localhost:3000'
    : process.env.REACT_APP_API_URL;
};

/**
 * Parse URL parameters
 */
function parseUrlParams(searchParams) {
  const monthsParam = searchParams.get('months');
  const hoursParam = searchParams.get('hours');
  const cellIdParam = searchParams.get('cell_id');

  const months = monthsParam ? monthsParam.split(',').map(Number).filter(n => !isNaN(n)) : null;
  const hours = hoursParam ? hoursParam.split(',').map(Number).filter(n => !isNaN(n)) : null;
  const cell_id = cellIdParam && !isNaN(Number(cellIdParam)) ? cellIdParam : null;

  return { months, hours, cell_id };
}

/**
 * Update URL parameters
 */
function updateUrlParams(navigate, scenario_id, months, hours, cell_id) {
  const monthsStr = months.join(',');
  const hoursStr = hours.join(',');
  navigate(`/depth_occupancy/${scenario_id}?months=${monthsStr}&hours=${hoursStr}&cell_id=${cell_id}`, { replace: true });
}

/**
 * Load global data for the scenario
 */
async function loadGlobalData(scenario_id) {
  const apiBaseUrl = getApiBaseUrl();

  try {
    const [scenarioRes, geometriesRes, cellDepthsRes, timestampsRes, minimumsRes] = await Promise.all([
      axios.get(`${apiBaseUrl}/v1/depth/scenario/${scenario_id}/scenario`),
      axios.get(`${apiBaseUrl}/v1/depth/scenario/${scenario_id}/geometries`),
      axios.get(`${apiBaseUrl}/v1/depth/scenario/${scenario_id}/cell_depths`),
      axios.get(`${apiBaseUrl}/v1/depth/scenario/${scenario_id}/timestamps`),
      axios.get(`${apiBaseUrl}/v1/depth/scenario/${scenario_id}/minimums`)
    ]);

    // Filter minimums to only include the deepest depth bin for each cell
    const filteredMinimums = {};
    const cellDepths = cellDepthsRes.data;

    Object.keys(minimumsRes.data).forEach(cellId => {
      const depthBin = cellDepths[cellId];
      if (depthBin !== undefined && minimumsRes.data[cellId][depthBin]) {
        filteredMinimums[cellId] = minimumsRes.data[cellId][depthBin];
      }
    });

    return {
      scenario: scenarioRes.data,
      geometries: geometriesRes.data,
      cell_depths: cellDepths,
      timestamps: timestampsRes.data,
      minimums: filteredMinimums
    };
  } catch (error) {
    console.error('Error loading global data:', error);
    throw new Error(error.response?.data?.message || error.message || 'Failed to load scenario data');
  }
}

/**
 * Load occupancy data for a specific cell
 */
async function loadOccupancy(scenario_id, cell_id, cell_depths, occupancy_data) {
  // Skip if already loaded
  if (occupancy_data[cell_id]) {
    return;
  }

  const apiBaseUrl = getApiBaseUrl();
  const depth_bin = cell_depths[cell_id];

  try {
    const response = await axios.get(
      `${apiBaseUrl}/v1/depth/scenario/${scenario_id}/occupancy?cell_id=${cell_id}&depth_bin=${depth_bin}`
    );

    occupancy_data[cell_id] = response.data;
  } catch (error) {
    console.error(`Error loading occupancy for cell ${cell_id}:`, error);
    throw new Error(error.response?.data?.message || error.message || 'Failed to load occupancy data');
  }
}

/**
 * Filter data by selected months
 */
function filterByMonth(timestamps, selected_months, occupancy_data) {
  const filtered_indices = [];

  timestamps.forEach((timestamp, index) => {
    const date = new Date(timestamp.replace(' ', 'T') + 'Z');
    const month = date.getUTCMonth() + 1; // Convert to 1-based

    if (selected_months.includes(month)) {
      filtered_indices.push(index);
    }
  });

  const filtered_timestamps = filtered_indices.map(i => timestamps[i]);

  const filtered_occupancy_data = {};
  Object.keys(occupancy_data).forEach(cell_id => {
    filtered_occupancy_data[cell_id] = occupancy_data[cell_id].map(line =>
      filtered_indices.map(i => line[i])
    );
  });

  return { filtered_timestamps, filtered_occupancy_data };
}

/**
 * Build highlighted indices from filtered timestamps and selected hours
 */
function buildHighlightIndices(filtered_timestamps, selected_hours) {
  const highlighted_indices = [];

  filtered_timestamps.forEach((timestamp, index) => {
    const date = new Date(timestamp.replace(' ', 'T') + 'Z');
    const hour = date.getUTCHours();

    if (selected_hours.includes(hour)) {
      highlighted_indices.push(index);
    }
  });

  return highlighted_indices;
}

/**
 * Calculate filtered minimums based on selected months and hours
 */
function calculateFilteredMinimums(minimums, selectedMonths, selectedHours) {
  const filtered_minimums = {};

  Object.keys(minimums).forEach(cell_id => {
    const month_data = minimums[cell_id];
    let min_value = Infinity;

    selectedMonths.forEach(month => {
      const hour_array = month_data[month];
      if (hour_array) {
        selectedHours.forEach(hour => {
          if (hour_array[hour] !== undefined && hour_array[hour] !== null) {
            min_value = Math.min(min_value, hour_array[hour]);
          }
        });
      }
    });

    filtered_minimums[cell_id] = min_value === Infinity ? null : min_value;
  });

  return filtered_minimums;
}

/**
 * DepthOccupancyReport Component
 */
const DepthOccupancyReport = () => {
  const { scenario_id } = useParams();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  // State
  const [scenario, setScenario] = useState(null);
  const [geometries, setGeometries] = useState(null);
  const [cellDepths, setCellDepths] = useState({});
  const [timestamps, setTimestamps] = useState([]);
  const [minimums, setMinimums] = useState({});
  const [occupancyData, setOccupancyData] = useState({});

  const [selectedMonths, setSelectedMonths] = useState([1, 2, 3, 4]);
  const [selectedHours, setSelectedHours] = useState([6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]);
  const [selectedCells, setSelectedCells] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [occupancyError, setOccupancyError] = useState(null);

  // Load global data on mount
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const data = await loadGlobalData(scenario_id);

        setScenario(data.scenario);
        setGeometries(data.geometries);
        setCellDepths(data.cell_depths);
        setTimestamps(data.timestamps);
        setMinimums(data.minimums);

        // Parse URL params or use defaults
        const urlParams = parseUrlParams(searchParams);

        if (urlParams.months) {
          setSelectedMonths(urlParams.months);
        }

        if (urlParams.hours) {
          setSelectedHours(urlParams.hours);
        }

        // Set initial selected cell
        const initialCellId = urlParams.cell_id || Object.keys(data.cell_depths)[0];
        if (initialCellId) {
          setSelectedCells([initialCellId]);
        }

        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    loadData();
  }, [scenario_id, searchParams]);

  // Load occupancy data when cell selection changes
  useEffect(() => {
    const loadCellOccupancy = async () => {
      if (selectedCells.length > 0 && cellDepths && Object.keys(cellDepths).length > 0) {
        const cellId = selectedCells[0];
        try {
          await loadOccupancy(scenario_id, cellId, cellDepths, occupancyData);
          setOccupancyData({ ...occupancyData }); // Trigger re-render
          setOccupancyError(null);
        } catch (err) {
          setOccupancyError(err.message);
        }
      }
    };

    loadCellOccupancy();
  }, [selectedCells, scenario_id, cellDepths]);

  // Update URL when selections change
  useEffect(() => {
    if (selectedCells.length > 0 && selectedMonths.length > 0 && selectedHours.length > 0) {
      updateUrlParams(navigate, scenario_id, selectedMonths, selectedHours, selectedCells[0]);
    }
  }, [selectedMonths, selectedHours, selectedCells, navigate, scenario_id]);

  // Calculate derived data
  const filteredMinimums = minimums && selectedMonths && selectedHours
    ? calculateFilteredMinimums(minimums, selectedMonths, selectedHours)
    : {};

  const { filtered_timestamps, filtered_occupancy_data } = timestamps && occupancyData && selectedMonths
    ? filterByMonth(timestamps, selectedMonths, occupancyData)
    : { filtered_timestamps: [], filtered_occupancy_data: {} };

  const highlight_indices = filtered_timestamps && selectedHours
    ? buildHighlightIndices(filtered_timestamps, selectedHours)
    : [];

  // Handle navigation
  const handleBack = () => {
    navigate('/');
  };

  const handleHome = () => {
    navigate('/');
  };

  const handleRetryGlobal = () => {
    setError(null);
    window.location.reload();
  };

  const handleRetryOccupancy = () => {
    setOccupancyError(null);
    setOccupancyData({});
  };

  if (loading) {
    return (
      <div className="depth-occupancy-report__loading">
        Loading...
      </div>
    );
  }

  if (error) {
    return (
      <ErrorPopup
        message="Failed to load data"
        details={error}
        onRetry={handleRetryGlobal}
        onClose={handleRetryGlobal}
      />
    );
  }

  return (
    <div className="depth-occupancy-report">
      {occupancyError && (
        <ErrorPopup
          message="Failed to load occupancy data"
          details={occupancyError}
          onRetry={handleRetryOccupancy}
          onClose={() => setOccupancyError(null)}
        />
      )}

      <div className="depth-occupancy-report__title-bar">
        <TitleBar
          scenarioName={scenario?.name || ''}
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
            values={filteredMinimums}
            geojson={geometries}
            unit="Minimum Likelihood of Occupancy"
            lowColor="#e8f4f8"
            highColor="#1589b0"
            selectedCells={selectedCells}
            setSelectedCells={setSelectedCells}
            center={scenario?.center || [0, 0]}
            zoom={scenario?.zoom || 10}
            legend_size="medium"
            legend_layout="vertical"
            legend_background="#ffffff"
          />
        )}
      </div>

      <div className="depth-occupancy-report__contour-date-graph">
        {selectedCells.length > 0 && filtered_occupancy_data[selectedCells[0]] && (
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
        )}
      </div>
    </div>
  );
};

export default DepthOccupancyReport;
