import * as d3 from 'd3';

/**
 * Interpolates colors for values based on a color scale.
 *
 * @param {string} lowColor - Hex color for the low end of values
 * @param {string} highColor - Hex color for the high end of values
 * @param {number[]} values - Array of numeric values to interpolate colors for (may not be in order)
 * @returns {string[]} Array of hex colors, one for each value
 */
export function interpolateColor(lowColor, highColor, values) {
  // Filter out null/undefined values for finding min/max
  const validValues = values.filter(v => v !== null && v !== undefined);

  if (validValues.length === 0) {
    return values.map(() => null);
  }

  const minValue = Math.min(...validValues);
  const maxValue = Math.max(...validValues);

  // Create d3 color interpolator
  const colorInterpolator = d3.interpolate(lowColor, highColor);

  // Map each value to a color
  return values.map(value => {
    if (value === null || value === undefined) {
      return null;
    }

    // Handle edge case where all values are the same
    if (maxValue === minValue) {
      return colorInterpolator(0.5);
    }

    // Normalize value to 0-1 range
    const normalizedValue = (value - minValue) / (maxValue - minValue);
    return colorInterpolator(normalizedValue);
  });
}

/**
 * Builds a color scale array for display in a MapLegend.
 *
 * @param {number[]} quantiles - Array of quantile values (e.g., [0, 25, 50, 75, 100])
 * @param {number[]} values - Array of numeric values
 * @param {string[]} colors - Array of hex colors corresponding to values
 * @returns {Array<[string, string]>} Array of [label, color] tuples for MapLegend
 */
export function buildColorScale(quantiles, values, colors) {
  // Filter out null/undefined values
  const validEntries = values
    .map((value, index) => ({ value, color: colors[index] }))
    .filter(entry => entry.value !== null && entry.value !== undefined);

  if (validEntries.length === 0) {
    return [];
  }

  // Sort by value
  validEntries.sort((a, b) => a.value - b.value);

  const sortedValues = validEntries.map(e => e.value);
  const sortedColors = validEntries.map(e => e.color);

  const colorScale = [];

  for (let i = 0; i < quantiles.length; i++) {
    const quantile = quantiles[i];

    // Calculate the index for this quantile
    const index = Math.floor((quantile / 100) * (sortedValues.length - 1));
    const value = sortedValues[index];
    const color = sortedColors[index];

    // Format label
    const label = value.toFixed(3);

    colorScale.push([label, color]);
  }

  return colorScale;
}
