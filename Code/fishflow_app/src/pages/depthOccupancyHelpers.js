import axios from 'axios';

/**
 * Gets the API base URL based on environment configuration.
 *
 * @returns {string} The base URL for API requests
 */
export const getApiBaseUrl = () => {
  return process.env.REACT_APP_FISHFLOW_MODE === 'DEV'
    ? 'http://localhost:8000'
    : process.env.REACT_APP_API_URL;
};

/**
 * Loads global data for a depth occupancy scenario.
 *
 * Fetches scenario metadata, geometries, cell depths, timestamps, and minimums
 * from the FishFlow API.
 *
 * @param {string} scenarioId - The ID of the scenario to load
 * @returns {Promise<Object>} Object containing scenario, geometries, cell_depths, timestamps, minimums
 * @throws {Error} If any API request fails
 */
export async function loadGlobalData(scenarioId) {
  const baseUrl = getApiBaseUrl();

  try {
    // Fetch all global data in parallel
    const [
      scenarioResponse,
      geometriesResponse,
      cellDepthsResponse,
      timestampsResponse,
      minimumsResponse
    ] = await Promise.all([
      axios.get(`${baseUrl}/v1/depth/scenario/${scenarioId}/scenario`),
      axios.get(`${baseUrl}/v1/depth/scenario/${scenarioId}/geometries`),
      axios.get(`${baseUrl}/v1/depth/scenario/${scenarioId}/cell_depths`),
      axios.get(`${baseUrl}/v1/depth/scenario/${scenarioId}/timestamps`),
      axios.get(`${baseUrl}/v1/depth/scenario/${scenarioId}/minimums`)
    ]);

    const scenario = scenarioResponse.data;
    const geometries = geometriesResponse.data;
    const cell_depths = cellDepthsResponse.data;
    const timestamps = timestampsResponse.data;
    const minimumsRaw = minimumsResponse.data;

    // Filter minimums to only include the deepest depth bin per cell
    const minimums = {};
    for (const [cellId, depthBins] of Object.entries(minimumsRaw)) {
      const depthBin = cell_depths[cellId];
      if (depthBins[depthBin]) {
        minimums[cellId] = depthBins[depthBin];
      }
    }

    return {
      scenario,
      geometries,
      cell_depths,
      timestamps,
      minimums
    };
  } catch (error) {
    throw new Error(`Failed to load global data: ${error.message}`);
  }
}

/**
 * Loads occupancy data for a specific cell.
 *
 * Fetches the occupancy timeline for a cell at its maximum depth bin.
 * Updates occupancy_data object in place if the cell data isn't already loaded.
 *
 * @param {string} scenarioId - ID of the scenario
 * @param {string} cellId - ID of the cell to load
 * @param {Object.<string, number>} cell_depths - Object mapping cell_id to depth_bin
 * @param {Object.<string, Array.<Array.<number>>>} occupancy_data - Object to update with occupancy data
 * @returns {Promise<void>}
 * @throws {Error} If API request fails
 */
export async function loadOccupancy(scenarioId, cellId, cell_depths, occupancy_data) {
  // Skip if already loaded
  if (occupancy_data[cellId]) {
    return;
  }

  const baseUrl = getApiBaseUrl();
  const depthBin = cell_depths[cellId];

  try {
    const response = await axios.get(
      `${baseUrl}/v1/depth/scenario/${scenarioId}/occupancy`,
      {
        params: {
          cell_id: cellId,
          depth_bin: depthBin
        }
      }
    );

    // Store the occupancy data (array of arrays, unwrapped from API)
    occupancy_data[cellId] = response.data;
  } catch (error) {
    throw new Error(`Failed to load occupancy for cell ${cellId}: ${error.message}`);
  }
}

/**
 * Filters timestamps and occupancy data by selected months.
 *
 * @param {string[]} timestamps - Array of ISO 8601 datetime strings
 * @param {number[]} selectedMonths - Array of month numbers (1-12)
 * @param {Object.<string, Array.<Array.<number>>>} occupancy_data - Cell occupancy data
 * @returns {Object} Object with filtered_timestamps and filtered_occupancy_data
 */
export function filterByMonth(timestamps, selectedMonths, occupancy_data) {
  // Find indices of timestamps matching selected months
  const filteredIndices = [];
  const filtered_timestamps = [];

  timestamps.forEach((timestamp, index) => {
    const date = new Date(timestamp);
    const month = date.getMonth() + 1; // getMonth() returns 0-11

    if (selectedMonths.includes(month)) {
      filteredIndices.push(index);
      filtered_timestamps.push(timestamp);
    }
  });

  // Filter occupancy data for all cells
  const filtered_occupancy_data = {};

  for (const [cellId, occupancy] of Object.entries(occupancy_data)) {
    // Filter each model's timeline
    filtered_occupancy_data[cellId] = occupancy.map(modelTimeline =>
      filteredIndices.map(i => modelTimeline[i])
    );
  }

  return {
    filtered_timestamps,
    filtered_occupancy_data
  };
}

/**
 * Builds an array of indices for highlighted timestamps based on selected hours.
 *
 * @param {string[]} filtered_timestamps - Array of ISO 8601 datetime strings
 * @param {number[]} selectedHours - Array of hour numbers (0-23)
 * @returns {number[]} Array of indices to highlight
 */
export function buildHighlightIndices(filtered_timestamps, selectedHours) {
  const highlightIndices = [];

  filtered_timestamps.forEach((timestamp, index) => {
    const date = new Date(timestamp);
    const hour = date.getHours();

    if (selectedHours.includes(hour)) {
      highlightIndices.push(index);
    }
  });

  return highlightIndices;
}

/**
 * Calculates minimum occupancy values per cell for selected months and hours.
 *
 * @param {Object} minimums - Nested object: cell_id -> depth_bin -> month -> hour_array
 * @param {Object.<string, number>} cell_depths - Object mapping cell_id to depth_bin
 * @param {number[]} selectedMonths - Array of month numbers (1-12)
 * @param {number[]} selectedHours - Array of hour numbers (0-23)
 * @returns {Object.<string, number>} Object mapping cell_id to minimum occupancy value
 */
export function calculateFilteredMinimums(minimums, cell_depths, selectedMonths, selectedHours) {
  const filtered_minimums = {};

  for (const [cellId, depthBins] of Object.entries(minimums)) {
    const depthBin = cell_depths[cellId];
    const monthData = depthBins[depthBin];

    if (!monthData) {
      continue;
    }

    let minValue = Infinity;

    for (const month of selectedMonths) {
      const hourArray = monthData[month];
      if (!hourArray) {
        continue;
      }

      for (const hour of selectedHours) {
        if (hour < hourArray.length) {
          minValue = Math.min(minValue, hourArray[hour]);
        }
      }
    }

    filtered_minimums[cellId] = minValue === Infinity ? 0 : minValue;
  }

  return filtered_minimums;
}

/**
 * Parses URL query parameters for months, hours, and cell_id.
 *
 * @param {URLSearchParams} searchParams - URLSearchParams from React Router
 * @returns {Object} Object with months, hours, and cell_id (or null if not present)
 */
export function parseUrlParams(searchParams) {
  let months = null;
  let hours = null;
  let cell_id = null;

  try {
    const monthsParam = searchParams.get('months');
    if (monthsParam) {
      months = monthsParam.split(',').map(m => parseInt(m, 10)).filter(m => !isNaN(m) && m >= 1 && m <= 12);
      if (months.length === 0) months = null;
    }
  } catch (e) {
    months = null;
  }

  try {
    const hoursParam = searchParams.get('hours');
    if (hoursParam) {
      hours = hoursParam.split(',').map(h => parseInt(h, 10)).filter(h => !isNaN(h) && h >= 0 && h <= 23);
      if (hours.length === 0) hours = null;
    }
  } catch (e) {
    hours = null;
  }

  try {
    const cellIdParam = searchParams.get('cell_id');
    if (cellIdParam) {
      const parsed = parseInt(cellIdParam, 10);
      if (!isNaN(parsed)) {
        cell_id = String(parsed);
      }
    }
  } catch (e) {
    cell_id = null;
  }

  return { months, hours, cell_id };
}

/**
 * Updates URL query parameters without creating browser history entry.
 *
 * @param {Function} navigate - React Router navigate function
 * @param {string} scenarioId - Current scenario ID
 * @param {number[]} months - Selected month numbers (1-12)
 * @param {number[]} hours - Selected hour numbers (0-23)
 * @param {string} cellId - Selected cell ID
 */
export function updateUrlParams(navigate, scenarioId, months, hours, cellId) {
  const monthsStr = months.join(',');
  const hoursStr = hours.join(',');
  navigate(
    `/depth_occupancy/${scenarioId}?months=${monthsStr}&hours=${hoursStr}&cell_id=${cellId}`,
    { replace: true }
  );
}
