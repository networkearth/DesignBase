## `ContourDateGraph`
`fishflow_app/src/components/plotting/ContourDateGraph.jsx`

```jsx
<ContourDateGraph
  complete_y={[[10, 20, 30, 40, 50], [15, 25, 35, 45, 55], [12, 22, 32, 42, 52]]}
  complete_x={['2024-01-01T00:00:00Z', '2024-01-02T00:00:00Z', '2024-01-03T00:00:00Z', '2024-01-04T00:00:00Z', '2024-01-05T00:00:00Z']}
  highlight_indices={[1, 2, 3]}
  support={[0.8, 0.6, 0.9]}
  x_label="Date"
  y_label="Value"
  title="Forecast Lines"
  size="medium"
/>
```

- **@input** `complete_y` - Array of arrays. Each inner array is a line (ordered by `support`) containing y values
- **@input** `complete_x` - Single array of datetime values (x-axis), shared across all complete lines. Values are sorted.
- **@input** `highlight_indices` - Array of indices. These indices are used internally to generate `highlight_x` and `highlight_y` from `complete_x` and `complete_y`.
- **@data** `highlight_y` - Array of arrays. Each inner array is a line (ordered by `support`) containing y values for highlighted segments. Derived internally from `complete_y` using `highlight_indices`.
- **@data** `highlight_x` - Single array of datetime values (x-axis), shared across all highlight lines. Values are sorted. Derived internally from `complete_x` using `highlight_indices`.
- **@input** `support` - Array of support values, one per line. Arbitrary numeric values.
- **@input** `x_label` - String label for x-axis
- **@input** `y_label` - String label for y-axis
- **@input** `title` - String title displayed in top right corner within plot area
- **@input** `size` - `"small"` | `"medium"` | `"large"` - Controls text sizing only (default: `"medium"`)
- **@state** `hoveredLine` - Tracks which line (index and type: complete/highlight) is currently being hovered
#### Notes

The idea here is to show a series of lines (over dates) where each line has a specific support and certain sections of those lines are highlighted for contrast. 

**Line Rendering**

- Two sets of lines are rendered: complete (grey) and highlighted (blue)
- Complete lines span the full x-axis range
- Highlighted lines are incomplete segments used to emphasize specific x-axis ranges
- All highlighted lines render on top of complete lines

**Support-Based Opacity**

- Each line's opacity is determined by its support value
- Higher support → higher opacity (maximum support = full opacity)
- Lower support → lower opacity (minimum support = minimum visible opacity)
- Opacity scales linearly between minimum and maximum support values

**Hover Tooltip**

- Hovering over any line displays a tooltip showing data for the specific hovered line at the hover point:
    - x value at hover point (datetime)
    - y value at hover point for the specific line being hovered (rounded to 3 decimal places)
    - support value for the specific line being hovered (rounded to 3 decimal places)
- Tooltip appears immediately at mouse position with no transition animation
- Tooltip positioning includes boundary detection to prevent tooltip from extending off-screen
- Visual indicator (dot) appears on the hovered line at the exact hover point to clearly identify which line is being hovered
- Dot size scales with component size (small/medium/large)
- Tooltip must track which specific line is being hovered to display the correct y and support values for that line
- Line hover detection: When lines are not directly overlapping, select the line nearest to cursor position. When lines are exactly overlapping, use simplest implementation (first match or rendering order)

##### How to Build It

Uses `recharts` library for chart rendering with:

- Line components for each complete and highlighted line
- Cartesian grid for gridlines
- Axes with labels
- Tooltip component for hover interactions with instant positioning
- Active dot indicator on hovered line
- Hover state tracking to identify which specific line is being interacted with
##### Constraints

**Data Constraints:**

- `complete_y`, `highlight_y`, and `support` have the same length and ordering
- `complete_x` and `highlight_x` are sorted datetime arrays
- Lines correspond by index: `complete_y[i]`, `highlight_y[i]`, and `support[i]` represent the same line
- All highlighted lines share the same `highlight_x` array

**Opacity Calculation**

- Calculate min and max support values from `support` array
- For each line, map its support value to opacity range (e.g., 0.3 to 1.0)
- Formula: `opacity = minOpacity + (support - minSupport) / (maxSupport - minSupport) * (1 - minOpacity)`
- Edge case: If all support values are identical (`maxSupport === minSupport`), default all lines to the same opacity (1.0)

**Data Formatting**

- Format datetime values for x-axis display using `"MMM d"` format (e.g., "Jan 1", "Feb 15")
- Round y-axis tick values to 3 decimal places
- Round tooltip y and support values to 3 decimal places

**Tooltip Data Extraction**

- Track the specific line index being hovered using hover state
- Extract the exact x value at the hover point
- Extract the y value for the specific hovered line at that x position (using the line index from hover state)
- Retrieve the corresponding support value for the hovered line
- Display all values in tooltip rounded to 3 decimal places
- CRITICAL: Must use the line index from hover state to get the correct y value, not the default payload value from Recharts
##### Styling

**Component Layout**

- Fills 100% width and height of parent `<div>`
- Maintains aspect ratio based on container dimensions

**Colors**

- Complete lines: `#adb5bd` (Bootstrap light grey)
- Highlighted lines: `#0d6efd` (Bootstrap blue)
- Text: `#212529`
- Background: `#ffffff`
- Grid lines: `#e9ecef` (light grey)
- Hover dot: Matches line color (grey or blue)

**Line Styling**

- Stroke width: 2px (small), 2.5px (medium), 3px (large)
- Opacity: Calculated from support values (0.3 minimum to 1.0 maximum)
- Smooth curves between data points
- Active dot radius: 4px (small), 5px (medium), 6px (large)

**Size Variations**

- **Small**: 0.875rem (14px) font, 0.5rem padding
- **Medium** (default): 1rem (16px) font, 0.75rem padding
- **Large**: 1.25rem (20px) font, 1rem padding

**Tooltip Styling**

- Background: `#212529`
- Text color: `#ffffff`
- Font size: 0.875rem
- Padding: 0.5rem
- Border radius: 0.25rem
- Appears instantly at mouse position with no animation/transition
- Format:
    
    ```
    x: [datetime at hover point]y: [value at hover point for hovered line to 3 decimals]support: [value for hovered line to 3 decimals]
    ```
    

**Title Styling**

- Position: Top right corner of plot area
- Font weight: 500
- Color: `#212529`
- Margin bottom: 0.75rem

**Axis Styling**

- X-axis: Datetime ticks (one per date)
- Y-axis: Values rounded to 3 decimal places
- Axis labels use size-appropriate font sizing

**Typography**

- Font family: `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif`
- Title font-weight: `500`

**Accessibility**

- ARIA labels for chart and axes
- Keyboard navigable tooltip
- Sufficient color contrast
- Semantic structure