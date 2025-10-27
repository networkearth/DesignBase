import React, { useState, useMemo } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import './ContourDateGraph.css';

/**
 * ContourDateGraph Component
 *
 * Shows a series of lines over dates where each line has a specific support
 * and certain sections are highlighted for contrast.
 *
 * @param {number[][]} complete_y - Array of arrays, each inner array is a line with y values
 * @param {string[]} complete_x - Array of datetime values (x-axis), shared across all lines
 * @param {number[]} highlight_indices - Array of indices to highlight from complete data
 * @param {number[]} support - Array of support values, one per line
 * @param {string} x_label - Label for x-axis
 * @param {string} y_label - Label for y-axis
 * @param {string} title - Title displayed in top right corner
 * @param {string} size - "small" | "medium" | "large" - Controls text sizing
 */
const ContourDateGraph = ({
  complete_y,
  complete_x,
  highlight_indices,
  support,
  x_label,
  y_label,
  title,
  size = 'medium'
}) => {
  const [hoveredLine, setHoveredLine] = useState(null);

  // Size configurations
  const sizeConfig = {
    small: { fontSize: '0.875rem', padding: '0.5rem', strokeWidth: 2, dotRadius: 4 },
    medium: { fontSize: '1rem', padding: '0.75rem', strokeWidth: 2.5, dotRadius: 5 },
    large: { fontSize: '1.25rem', padding: '1rem', strokeWidth: 3, dotRadius: 6 }
  };

  const config = sizeConfig[size];

  // Calculate opacity for each line based on support
  const calculateOpacity = (supportValue) => {
    if (!support || support.length === 0) return 1;

    const minSupport = Math.min(...support);
    const maxSupport = Math.max(...support);

    // If all support values are the same, return full opacity
    if (maxSupport === minSupport) return 1;

    const minOpacity = 0.3;
    return minOpacity + (supportValue - minSupport) / (maxSupport - minSupport) * (1 - minOpacity);
  };

  // Derive highlight_y and highlight_x from complete data using highlight_indices
  const highlight_y = useMemo(() => {
    if (!highlight_indices || highlight_indices.length === 0) return [];
    return complete_y.map(line => highlight_indices.map(idx => line[idx]));
  }, [complete_y, highlight_indices]);

  const highlight_x = useMemo(() => {
    if (!highlight_indices || highlight_indices.length === 0) return [];
    return highlight_indices.map(idx => complete_x[idx]);
  }, [complete_x, highlight_indices]);

  // Format data for Recharts
  const completeData = useMemo(() => {
    return complete_x.map((x, index) => {
      const dataPoint = { x, index };
      complete_y.forEach((line, lineIndex) => {
        dataPoint[`line_${lineIndex}`] = line[index];
      });
      return dataPoint;
    });
  }, [complete_x, complete_y]);

  const highlightData = useMemo(() => {
    if (!highlight_x || highlight_x.length === 0) return [];
    return highlight_x.map((x, index) => {
      const dataPoint = { x, index };
      highlight_y.forEach((line, lineIndex) => {
        dataPoint[`line_${lineIndex}`] = line[index];
      });
      return dataPoint;
    });
  }, [highlight_x, highlight_y]);

  // Format date for x-axis
  const formatDate = (dateString) => {
    const date = new Date(dateString.replace(' ', 'T') + 'Z');
    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    return `${monthNames[date.getUTCMonth()]} ${date.getUTCDate()}`;
  };

  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }) => {
    if (!active || !payload || payload.length === 0) return null;

    // Find which line is being hovered
    if (hoveredLine === null) return null;

    const lineData = payload.find(p => p.dataKey === `line_${hoveredLine.lineIndex}`);
    if (!lineData) return null;

    return (
      <div className="contour-date-graph__tooltip">
        <div>x: {formatDate(label)}</div>
        <div>y: {lineData.value.toFixed(3)}</div>
        <div>support: {support[hoveredLine.lineIndex].toFixed(3)}</div>
      </div>
    );
  };

  return (
    <div className="contour-date-graph" style={{ fontSize: config.fontSize, padding: config.padding }}>
      {title && <div className="contour-date-graph__title">{title}</div>}
      <ResponsiveContainer width="100%" height="100%">
        <LineChart margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e9ecef" />
          <XAxis
            dataKey="x"
            tickFormatter={formatDate}
            label={{ value: x_label, position: 'insideBottom', offset: -50 }}
            type="category"
            allowDuplicatedCategory={false}
          />
          <YAxis
            label={{ value: y_label, angle: -90, position: 'insideLeft' }}
            tickFormatter={(value) => value.toFixed(3)}
          />
          <Tooltip content={<CustomTooltip />} />

          {/* Render complete lines (grey) */}
          {complete_y.map((_, lineIndex) => (
            <Line
              key={`complete-${lineIndex}`}
              data={completeData}
              dataKey={`line_${lineIndex}`}
              stroke="#adb5bd"
              strokeWidth={config.strokeWidth}
              strokeOpacity={calculateOpacity(support[lineIndex])}
              dot={false}
              activeDot={{
                r: config.dotRadius,
                onMouseEnter: () => setHoveredLine({ lineIndex, type: 'complete' }),
                onMouseLeave: () => setHoveredLine(null)
              }}
              isAnimationActive={false}
            />
          ))}

          {/* Render highlighted lines (blue) on top */}
          {highlight_y.map((_, lineIndex) => (
            <Line
              key={`highlight-${lineIndex}`}
              data={highlightData}
              dataKey={`line_${lineIndex}`}
              stroke="#0d6efd"
              strokeWidth={config.strokeWidth}
              strokeOpacity={calculateOpacity(support[lineIndex])}
              dot={false}
              activeDot={{
                r: config.dotRadius,
                onMouseEnter: () => setHoveredLine({ lineIndex, type: 'highlight' }),
                onMouseLeave: () => setHoveredLine(null)
              }}
              isAnimationActive={false}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ContourDateGraph;
