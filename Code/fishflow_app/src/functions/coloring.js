import * as d3 from 'd3';

/**
 * Interpolates colors for values between a low and high color.
 *
 * Creates a linear color scale mapping numeric values to hex colors.
 * Uses D3's scaleLinear to interpolate between lowColor and highColor
 * based on the min-max range of the provided values.
 *
 * @param {string} lowColor - Hex color code for the low end (e.g., '#e8f4f8')
 * @param {string} highColor - Hex color code for the high end (e.g., '#1589b0')
 * @param {Object.<string, number>} values - Object mapping cell_id to numeric value
 * @returns {Object.<string, string>} Object mapping cell_id to interpolated hex color
 *
 * @example
 * const colors = interpolateColor(
 *   '#e8f4f8',
 *   '#1589b0',
 *   { cell_1: 10, cell_2: 50, cell_3: 100 }
 * );
 * // Returns: { cell_1: '#e8f4f8', cell_2: '#7fbfd4', cell_3: '#1589b0' }
 */
export function interpolateColor(lowColor, highColor, values) {
  // Extract all numeric values
  const numericValues = Object.values(values);

  // Handle edge case of empty values
  if (numericValues.length === 0) {
    return {};
  }

  // Find min and max values
  const minValue = Math.min(...numericValues);
  const maxValue = Math.max(...numericValues);

  // Create D3 color scale
  const colorScale = d3.scaleLinear()
    .domain([minValue, maxValue])
    .range([lowColor, highColor]);

  // Map each cell_id's value to its interpolated color
  const colors = {};
  for (const [cellId, value] of Object.entries(values)) {
    colors[cellId] = colorScale(value);
  }

  return colors;
}

/**
 * Builds a color scale array for display in a MapLegend component.
 *
 * Calculates quantiles from the values and maps them to their corresponding
 * colors to create a legend showing the distribution of values.
 *
 * @param {number[]} quantiles - Array of quantile percentages (e.g., [0, 25, 50, 75, 100])
 * @param {Object.<string, number>} values - Object mapping cell_id to numeric value
 * @param {Object.<string, string>} colors - Object mapping cell_id to hex color string
 * @returns {Array.<Array.<string>>} Array of [label, color] tuples for MapLegend
 *
 * @example
 * const colorScale = buildColorScale(
 *   [0, 25, 50, 75, 100],
 *   { cell_1: 0.1, cell_2: 0.5, cell_3: 0.9 },
 *   { cell_1: '#e8f4f8', cell_2: '#7fbfd4', cell_3: '#1589b0' }
 * );
 * // Returns: [['0.1', '#e8f4f8'], ['0.3', '#...'], ['0.5', '#7fbfd4'], ...]
 */
export function buildColorScale(quantiles, values, colors) {
  // Extract all numeric values into an array
  const numericValues = Object.values(values);

  // Handle edge case of empty values
  if (numericValues.length === 0) {
    return [];
  }

  // Sort values for quantile calculation
  const sortedValues = numericValues.slice().sort((a, b) => a - b);

  const colorScale = [];

  // For each quantile percentage
  for (const quantilePercent of quantiles) {
    // Calculate the value at this quantile using D3
    const quantileValue = d3.quantile(sortedValues, quantilePercent / 100);

    // Find a cell_id that has this value (or closest to it)
    // We need to find the color corresponding to this value
    let closestCellId = null;
    let closestDiff = Infinity;

    for (const [cellId, value] of Object.entries(values)) {
      const diff = Math.abs(value - quantileValue);
      if (diff < closestDiff) {
        closestDiff = diff;
        closestCellId = cellId;
      }
    }

    // Get the color for this cell
    const color = colors[closestCellId];

    // Create label (round to 1 decimal place)
    const label = quantileValue.toFixed(1);

    // Add tuple to colorScale array
    colorScale.push([label, color]);
  }

  return colorScale;
}
