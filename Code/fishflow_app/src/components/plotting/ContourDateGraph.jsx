import React, { useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';
import { format } from 'date-fns';
import './ContourDateGraph.css';

/**
 * ContourDateGraph - Displays multiple forecast lines with support-based opacity.
 *
 * Shows complete and highlighted line segments with hover tooltips displaying
 * data for the specific hovered line.
 *
 * @param {Object} props
 * @param {Array.<Array.<number>>} props.complete_y - Array of arrays, each inner array is a line
 * @param {string[]} props.complete_x - Array of datetime values (ISO 8601 strings)
 * @param {number[]} props.highlight_indices - Indices to generate highlighted segments from
 * @param {number[]} props.support - Array of support values, one per line
 * @param {string} props.x_label - Label for x-axis
 * @param {string} props.y_label - Label for y-axis
 * @param {string} props.title - Title displayed in top right corner
 * @param {"small"|"medium"|"large"} [props.size="medium"] - Controls text sizing
 * @returns {JSX.Element}
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

  // Derive highlighted data from complete data using highlight_indices
  const highlight_x = highlight_indices.map(i => complete_x[i]);
  const highlight_y = complete_y.map(line => highlight_indices.map(i => line[i]));

  // Calculate opacity for each line based on support
  const calculateOpacity = (supportValue) => {
    if (support.length === 0) return 1.0;

    const minSupport = Math.min(...support);
    const maxSupport = Math.max(...support);

    // If all support values are identical, default to full opacity
    if (maxSupport === minSupport) return 1.0;

    const minOpacity = 0.3;
    return minOpacity + (supportValue - minSupport) / (maxSupport - minSupport) * (1 - minOpacity);
  };

  // Prepare data for recharts
  const completeData = complete_x.map((datetime, index) => {
    const dataPoint = { datetime, index };
    complete_y.forEach((line, lineIndex) => {
      dataPoint[`line_${lineIndex}`] = line[index];
    });
    return dataPoint;
  });

  const highlightData = highlight_x.map((datetime, index) => {
    const dataPoint = { datetime, index };
    highlight_y.forEach((line, lineIndex) => {
      dataPoint[`line_${lineIndex}`] = line[index];
    });
    return dataPoint;
  });

  // Size-based styling
  const sizeConfig = {
    small: { fontSize: '0.875rem', padding: '0.5rem', strokeWidth: 2, dotRadius: 4 },
    medium: { fontSize: '1rem', padding: '0.75rem', strokeWidth: 2.5, dotRadius: 5 },
    large: { fontSize: '1.25rem', padding: '1rem', strokeWidth: 3, dotRadius: 6 }
  };

  const config = sizeConfig[size];

  // Custom tooltip
  const CustomTooltip = ({ active, payload }) => {
    if (!active || !payload || payload.length === 0 || hoveredLine === null) {
      return null;
    }

    const { lineIndex, type } = hoveredLine;
    const dataPoint = payload[0].payload;
    const yValue = dataPoint[`line_${lineIndex}`];
    const supportValue = support[lineIndex];

    return (
      <div className="contour-date-graph__tooltip">
        <div>x: {format(new Date(dataPoint.datetime), 'MMM d')}</div>
        <div>y: {yValue?.toFixed(3) ?? 'N/A'}</div>
        <div>support: {supportValue?.toFixed(3) ?? 'N/A'}</div>
      </div>
    );
  };

  // Format x-axis ticks
  const formatXAxis = (datetime) => {
    try {
      return format(new Date(datetime), 'MMM d');
    } catch {
      return datetime;
    }
  };

  // Format y-axis ticks
  const formatYAxis = (value) => {
    return value.toFixed(3);
  };

  return (
    <div className="contour-date-graph" style={{ fontSize: config.fontSize, padding: config.padding }}>
      <div className="contour-date-graph__title">{title}</div>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart margin={{ top: 20, right: 30, left: 20, bottom: 50 }}>
          <CartesianGrid stroke="#e9ecef" strokeDasharray="3 3" />
          <XAxis
            dataKey="datetime"
            tickFormatter={formatXAxis}
            label={{ value: x_label, position: 'insideBottom', offset: -10 }}
            allowDuplicatedCategory={false}
          />
          <YAxis
            tickFormatter={formatYAxis}
            label={{ value: y_label, angle: -90, position: 'insideLeft' }}
          />
          <Tooltip content={<CustomTooltip />} />

          {/* Complete lines (grey) */}
          {complete_y.map((line, lineIndex) => (
            <Line
              key={`complete-${lineIndex}`}
              data={completeData}
              type="monotone"
              dataKey={`line_${lineIndex}`}
              stroke="#adb5bd"
              strokeWidth={config.strokeWidth}
              strokeOpacity={calculateOpacity(support[lineIndex])}
              dot={false}
              activeDot={{
                r: hoveredLine?.lineIndex === lineIndex && hoveredLine?.type === 'complete' ? config.dotRadius : 0
              }}
              onMouseEnter={() => setHoveredLine({ lineIndex, type: 'complete' })}
              onMouseLeave={() => setHoveredLine(null)}
            />
          ))}

          {/* Highlighted lines (blue) - render on top */}
          {highlight_y.map((line, lineIndex) => (
            <Line
              key={`highlight-${lineIndex}`}
              data={highlightData}
              type="monotone"
              dataKey={`line_${lineIndex}`}
              stroke="#0d6efd"
              strokeWidth={config.strokeWidth}
              strokeOpacity={calculateOpacity(support[lineIndex])}
              dot={false}
              activeDot={{
                r: hoveredLine?.lineIndex === lineIndex && hoveredLine?.type === 'highlight' ? config.dotRadius : 0
              }}
              onMouseEnter={() => setHoveredLine({ lineIndex, type: 'highlight' })}
              onMouseLeave={() => setHoveredLine(null)}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ContourDateGraph;
