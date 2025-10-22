import React, { useState, useMemo } from 'react';
import PropTypes from 'prop-types';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Label
} from 'recharts';

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

  // Size configuration
  const sizeConfig = {
    small: {
      fontSize: '0.875rem',
      padding: '0.5rem',
      strokeWidth: 2,
      dotRadius: 4
    },
    medium: {
      fontSize: '1rem',
      padding: '0.75rem',
      strokeWidth: 2.5,
      dotRadius: 5
    },
    large: {
      fontSize: '1.25rem',
      padding: '1rem',
      strokeWidth: 3,
      dotRadius: 6
    }
  };

  const config = sizeConfig[size];

  // Data processing functions
  const calculateOpacity = (supportValue, minSupport, maxSupport) => {
    const minOpacity = 0.3;
    if (maxSupport === minSupport) {
      return 1.0;
    }
    return minOpacity + (supportValue - minSupport) / (maxSupport - minSupport) * (1 - minOpacity);
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    return `${months[date.getMonth()]} ${date.getDate()}`;
  };

  // Derive highlight data from indices
  const { highlight_x, highlight_y } = useMemo(() => {
    const highlight_x = highlight_indices.map(idx => complete_x[idx]);
    const highlight_y = complete_y.map(line => highlight_indices.map(idx => line[idx]));
    return { highlight_x, highlight_y };
  }, [complete_x, complete_y, highlight_indices]);

  // Calculate opacities
  const opacities = useMemo(() => {
    const minSupport = Math.min(...support);
    const maxSupport = Math.max(...support);
    return support.map(s => calculateOpacity(s, minSupport, maxSupport));
  }, [support]);

  // Format data for recharts
  const completeData = useMemo(() => {
    return complete_x.map((x, idx) => {
      const point = { x };
      complete_y.forEach((line, lineIdx) => {
        point[`complete_${lineIdx}`] = line[idx];
      });
      return point;
    });
  }, [complete_x, complete_y]);

  const highlightData = useMemo(() => {
    return highlight_x.map((x, idx) => {
      const point = { x };
      highlight_y.forEach((line, lineIdx) => {
        point[`highlight_${lineIdx}`] = line[idx];
      });
      return point;
    });
  }, [highlight_x, highlight_y]);

  // Custom tooltip component
  const CustomTooltip = ({ active, payload, coordinate }) => {
    if (!active || !payload || !hoveredLine) return null;

    const { lineIndex, lineType } = hoveredLine;

    // Find the correct payload for the hovered line
    const hoveredPayload = payload.find(p => p.dataKey === `${lineType}_${lineIndex}`);
    if (!hoveredPayload) return null;

    const xValue = hoveredPayload.payload.x;
    const yValue = hoveredPayload.value;
    const supportValue = support[lineIndex];

    // Boundary detection
    let left = coordinate?.x || 0;
    let top = coordinate?.y || 0;

    const tooltipWidth = 200;
    const tooltipHeight = 80;
    const margin = 10;

    // Adjust for right boundary
    if (left + tooltipWidth + margin > window.innerWidth) {
      left = left - tooltipWidth - margin;
    } else {
      left = left + margin;
    }

    // Adjust for bottom boundary
    if (top + tooltipHeight + margin > window.innerHeight) {
      top = top - tooltipHeight - margin;
    } else {
      top = top + margin;
    }

    return (
      <div
        style={{
          position: 'fixed',
          left: `${left}px`,
          top: `${top}px`,
          backgroundColor: '#212529',
          color: '#ffffff',
          fontSize: '0.875rem',
          padding: '0.5rem',
          borderRadius: '0.25rem',
          pointerEvents: 'none',
          zIndex: 1000
        }}
      >
        <div>x: {formatDate(xValue)}</div>
        <div>y: {yValue.toFixed(3)}</div>
        <div>support: {supportValue.toFixed(3)}</div>
      </div>
    );
  };

  // Y-axis tick formatter
  const formatYAxis = (value) => {
    return value.toFixed(3);
  };

  return (
    <div style={{ width: '100%', height: '100%', position: 'relative' }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
          <CartesianGrid stroke="#e9ecef" />

          <XAxis
            dataKey="x"
            type="category"
            allowDuplicatedCategory={false}
            tickFormatter={formatDate}
            style={{ fontSize: config.fontSize, fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif' }}
          >
            <Label
              value={x_label}
              position="bottom"
              style={{ fontSize: config.fontSize, fill: '#212529' }}
            />
          </XAxis>

          <YAxis
            tickFormatter={formatYAxis}
            style={{ fontSize: config.fontSize, fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif' }}
          >
            <Label
              value={y_label}
              angle={-90}
              position="left"
              style={{ fontSize: config.fontSize, fill: '#212529', textAnchor: 'middle' }}
            />
          </YAxis>

          <Tooltip
            content={<CustomTooltip />}
            cursor={false}
            isAnimationActive={false}
          />

          {/* Render complete lines (grey) */}
          {complete_y.map((_, lineIdx) => (
            <Line
              key={`complete-${lineIdx}`}
              data={completeData}
              dataKey={`complete_${lineIdx}`}
              stroke="#adb5bd"
              strokeWidth={config.strokeWidth}
              strokeOpacity={opacities[lineIdx]}
              dot={false}
              activeDot={
                hoveredLine?.lineIndex === lineIdx && hoveredLine?.lineType === 'complete'
                  ? { r: config.dotRadius, fill: '#adb5bd' }
                  : false
              }
              type="monotone"
              onMouseEnter={() => setHoveredLine({ lineIndex: lineIdx, lineType: 'complete' })}
              onMouseLeave={() => setHoveredLine(null)}
            />
          ))}

          {/* Render highlight lines (blue) */}
          {highlight_y.map((_, lineIdx) => (
            <Line
              key={`highlight-${lineIdx}`}
              data={highlightData}
              dataKey={`highlight_${lineIdx}`}
              stroke="#0d6efd"
              strokeWidth={config.strokeWidth}
              strokeOpacity={opacities[lineIdx]}
              dot={false}
              activeDot={
                hoveredLine?.lineIndex === lineIdx && hoveredLine?.lineType === 'highlight'
                  ? { r: config.dotRadius, fill: '#0d6efd' }
                  : false
              }
              type="monotone"
              onMouseEnter={() => setHoveredLine({ lineIndex: lineIdx, lineType: 'highlight' })}
              onMouseLeave={() => setHoveredLine(null)}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>

      {/* Title overlay */}
      {title && (
        <div
          style={{
            position: 'absolute',
            top: config.padding,
            right: config.padding,
            fontSize: config.fontSize,
            fontWeight: 500,
            color: '#212529',
            pointerEvents: 'none',
            fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
          }}
        >
          {title}
        </div>
      )}
    </div>
  );
};

ContourDateGraph.propTypes = {
  complete_y: PropTypes.arrayOf(PropTypes.arrayOf(PropTypes.number)).isRequired,
  complete_x: PropTypes.arrayOf(PropTypes.string).isRequired,
  highlight_indices: PropTypes.arrayOf(PropTypes.number).isRequired,
  support: PropTypes.arrayOf(PropTypes.number).isRequired,
  x_label: PropTypes.string.isRequired,
  y_label: PropTypes.string.isRequired,
  title: PropTypes.string,
  size: PropTypes.oneOf(['small', 'medium', 'large'])
};

export default ContourDateGraph;
