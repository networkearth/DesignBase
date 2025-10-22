import { interpolateRgb, quantile } from 'd3';

/**
 * Interpolates colors between lowColor and highColor for given values
 * @param {string} lowColor - Hex color code for minimum value
 * @param {string} highColor - Hex color code for maximum value
 * @param {number[]} values - Array of numeric values to interpolate colors for
 * @returns {string[]} Array of hex color codes corresponding to each value
 */
export function interpolateColor(lowColor, highColor, values) {
  // Filter out null/undefined values for min/max calculation
  const validValues = values.filter(v => v != null);

  if (validValues.length === 0) {
    return values.map(() => null);
  }

  const minValue = Math.min(...validValues);
  const maxValue = Math.max(...validValues);

  // Create d3 color interpolator
  const colorInterpolator = interpolateRgb(lowColor, highColor);

  // Map each value to a color
  return values.map(value => {
    if (value == null) {
      return null;
    }

    // Handle edge case where all values are the same
    if (minValue === maxValue) {
      return colorInterpolator(0.5);
    }

    // Normalize value to 0-1 range and interpolate
    const t = (value - minValue) / (maxValue - minValue);
    return colorInterpolator(t);
  });
}

/**
 * Builds a color scale for MapLegend based on quantiles
 * @param {number[]} quantiles - Array of quantile percentages (e.g., [0, 25, 50, 75, 100])
 * @param {number[]} values - Array of numeric values
 * @param {string[]} colors - Array of color codes corresponding to values
 * @returns {Array<[string, string]>} Array of [label, color] tuples for MapLegend
 */
export function buildColorScale(quantiles, values, colors) {
  // Filter out null values and their corresponding colors
  const validPairs = values
    .map((value, index) => ({ value, color: colors[index] }))
    .filter(pair => pair.value != null);

  if (validPairs.length === 0) {
    return [];
  }

  const validValues = validPairs.map(p => p.value);

  // Calculate quantile values
  const colorScale = quantiles.map((q, index) => {
    const quantileValue = quantile(validValues, q / 100);

    // Find the color for this quantile value
    // Get the index in validValues closest to this quantile
    const sortedValidValues = [...validValues].sort((a, b) => a - b);
    const quantileIndex = Math.floor((q / 100) * (sortedValidValues.length - 1));
    const targetValue = sortedValidValues[quantileIndex];

    // Find the color corresponding to this value
    const colorIndex = validPairs.findIndex(p => p.value === targetValue);
    const color = colorIndex >= 0 ? validPairs[colorIndex].color : validPairs[0].color;

    // Format label
    let label;
    if (index === quantiles.length - 1) {
      label = `${quantileValue.toFixed(1)}+`;
    } else {
      const nextQuantileValue = quantile(validValues, quantiles[index + 1] / 100);
      label = `${quantileValue.toFixed(1)}-${nextQuantileValue.toFixed(1)}`;
    }

    return [label, color];
  });

  return colorScale;
}
