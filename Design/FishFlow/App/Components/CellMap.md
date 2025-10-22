## `MapLegend`

### Interfaces

```jsx
<MapLegend
  colorScale={[
    ['0-10', '#e8f4f8'],
    ['10-20', '#b3d9e6'],
    ['20-30', '#7fbfd4'],
    ['30-40', '#4aa4c2'],
    ['40+', '#1589b0']
  ]}
  unit="Temperature (°C)"
  size="medium"
  layout="vertical"
  background="#ffffff"
/>
```

- **@input** `colorScale` - Array of tuples `[label, color]` where label is a string and color is a hex code. Labels displayed in array order
- **@input** `unit` - String name of the unit being displayed (shown as title)
- **@style** `size` - `"x-small"` | `"small"` | `"medium"` | `"large"` - Controls sizing to work flexibly across screen sizes and parent components (default: `"medium"`)
- **@style** `layout` - `"vertical"` | `"horizontal"` - Determines arrangement of color swatches and labels (default: `"vertical"`)
- **@style** `background` - Hex color code for component background (default: `"#ffffff"`)
### Use Cases

A static react display component that provides a legend for map visualizations by showing color swatches paired with their corresponding labels.
### Build

- Should be a compact rectangle containing:
	- Unit name as the title
	- Color swatches paired with labels, displayed in the order provided

```bash
fishflow
|
+-- frontend
|   |
|   +-- src
|   |   |
|   |   +-- components
|   |   |   |
|   |   |   +-- mapping
|   |   |   |   |
|   |   |   |   +-- MapLegend.js <--
```
### Constraints

#### Styling

**Colors**
- Border: `#dee2e6`
- Text: `#212529`
- Background: Customizable via `background` prop (default: `#ffffff`)
- Color swatches: As specified in `colorScale` prop

**Size Variations**
- **X-Small**: 0.75rem (12px) font, 0.375rem padding, 0.75rem swatch size
- **Small**: 0.875rem (14px) font, 0.5rem padding, 1rem swatch size
- **Medium** (default): 1rem (16px) font, 0.75rem padding, 1.25rem swatch size
- **Large**: 1.25rem (20px) font, 1rem padding, 1.5rem swatch size

**Layout Styling**
- **Vertical**: Color swatches stacked vertically with labels to the right
- **Horizontal**: Color swatches arranged horizontally with labels below

**Component Styling**
- Border radius: `0.25rem`
- Border: `1px solid #dee2e6`
- Compact rectangular container
- Title (unit) displayed prominently at top/left depending on layout

**Spacing**
- Gap between swatches and labels: 0.5rem
- Gap between items: 0.25rem (x-small/small), 0.5rem (medium/large)
- Title margin: 0.5rem bottom (vertical), 0.5rem right (horizontal)

**Typography**
- Font family: `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif`
- Title font-weight: `500`
- Label font-weight: `400`

**Accessibility**
- Semantic HTML structure
- ARIA label describing the legend's purpose
- Sufficient color contrast for text

## `interpolateColor`

### Interfaces

```jsx
interpolateColor(lowColor, highColor, values, colors) --> colors
```

- **@input** `lowColor` - hash of the color for the low end of the values
- **@input** `highColor` - hash of the color for the high end of the values
- **@input** `values` - values over which to interpolate (note they may not be in order)
- **@returns** `colors` - colors for each value 

### Use Cases

Used to give colors to values given some color scale. 
### Build

Should use `d3` to interpolate between the colors given.
#### Placement

```bash
fishflow
|
+-- frontend
|   |
|   +-- src
|   |   |
|   |   +-- functions
|   |   |   |
|   |   |   +-- common
|   |   |   |   |
|   |   |   |   +-- coloring.js <--
```
### Constraints

N/A

## `buildColorScale`

### Interfaces

```jsx
buildColorScale(quantiles, values, colors) --> colorScale
```

- **@input** `quantiles` - the quantiles to build the color scale for
- **@input** `values` - the values
- **@input** `colors` - the colors associated with the values
- **@returns** `colorScale` - pairs of value-at-the-quantile, color-at-the-value that can be passed to a `MapLegend` component

### Use Cases

Builds a colorScale for a `MapLegend` given a set of values, colors, and the quantiles of interest.
### Build

#### Placement

```bash
fishflow
|
+-- frontend
|   |
|   +-- src
|   |   |
|   |   +-- functions
|   |   |   |
|   |   |   +-- common
|   |   |   |   |
|   |   |   |   +-- coloring.js <--
```
### Constraints

N/A

## `CellMap`

### Interfaces
```jsx
<CellMap
  allowMultiSelect={true}
  values={{ cell_1: 45.2, cell_2: 67.8, cell_3: null, cell_4: 23.1 }}
  geojson={...}
  unit="Temperature (°C)"
  lowColor="#e8f4f8"
  highColor="#1589b0"
  selectedCells={selectedCells}
  setSelectedCells={setSelectedCells}
  center={[40.7128, -74.0060]}
  zoom={10}
  legend_size="medium"
  legend_layout="vertical"
  legend_background="#ffffff"
/>
```

- **@input** `allowMultiSelect` - Boolean, whether multiple cell selection is allowed
- **@input** `values` - Object mapping `cell_id` to numeric value (nulls allowed)
- **@input** `geojson` - Geojson of polygons to display with a `cell_id` for each polygon
- **@input** `unit` - String, unit of measurement for values
- **@input** `lowColor` - Hex color code for minimum value
- **@input** `highColor` - Hex color code for maximum value
- **@input** `selectedCells` - Array of selected `cell_id` strings
- **@input** `setSelectedCells` - Setter function for `selectedCells`
- **@input** `center` - Array `[latitude, longitude]` for map center
- **@input** `zoom` - Number, initial zoom level
- **@input** `geometries` - GeoJSON geometries for cells
- **@style** `legend_size` - `"x-small"` | `"small"` | `"medium"` | `"large"` - Size for `MapLegend`
- **@style** `legend_layout` - `"vertical"` | `"horizontal"` - Layout for `MapLegend`
- **@style** `legend_background` - Hex color for `MapLegend` background
- **@product** `colors` - Object mapping `cell_id` to hex color based on value
- **@product** `colorScale` - Array of `[label, color]` tuples for `MapLegend`
- **@affects** `selectedCells`
### Use Cases

Displays polygons on a map colored by `values` and allows user to select specific cells for further drop down (implemented elsewhere in an app using a `CellMap`).

**Selection**
- `allowMultiSelect=true`: Users can select multiple cells. All selections added to `selectedCells`. A "Clear Selection" button appears in bottom right corner with same background color as `MapLegend`.
- `allowMultiSelect=false`: Each selection replaces the previous selection. `selectedCells` remains an array with single item.
- Clicking an already-selected cell deselects it.
- Selected cells display bold borders to indicate selection.

**Cell Hover**
When users hover over a cell, a tooltip displays the cell's value and unit directly over the mouse cursor.

**Re-Centering**
When new `geometries` are passed, map recenters to `center` and zooms to `zoom` level. Other interactions do not trigger re-centering to avoid user experience disruption.

### Build

**react-leaflet Map** (fills entire container)
- Displays polygons (cells) colored according to `colors`
- Selected cells have bold borders
- Null values result in no fill for that cell
- Fills entire parent `<div>`

**Color Interpolation**
```
lowColor + highColor + values → interpolateColor() → colors
```
- Interpolates colors between `lowColor` and `highColor` based on values
- Null values have no color assigned

**Color Scale Generation**
```
values + colors → buildColorScale(quantiles: 0, 25, 50, 75, 100) → colorScale
```
- Builds quantile-based color scale for legend
- Uses 0th, 25th, 50th, 75th, and 100th percentiles

**Re-center Effect**
- Watches `geometries` for changes
- When `geometries` changes, recenter map to `center` and zoom to `zoom`

**MapLegend** (top right corner)
- Uses `MapLegend` component with `colorScale`, `unit`, `legend_size`, `legend_layout`, `legend_background`

**Clear Selection Button** (bottom right corner)
- Only visible when `allowMultiSelect=true`
- Background color matches `MapLegend` background

#### Placement

```bash
fishflow
|
+-- frontend
|   |
|   +-- src
|   |   |
|   |   +-- components
|   |   |   |
|   |   |   +-- mapping
|   |   |   |   |
|   |   |   |   +-- CellMap.js <--
```

#### Dependencies

- `MapLegend`
- `interpolateColors`
- `buildColorScale`

### Constraints

#### Style

**Map Container**
- Fills 100% of parent `<div>` width and height

**Cell (Polygon) Styling**
- Fill: Color from `colors` object, or no fill if value is null
- Border: `1px solid #dee2e6` (normal state)
- Selected border: `3px solid #212529` (bold to indicate selection)
- Transition: `all 0.15s ease-in-out`

**Tooltip Styling**
- Background: `#212529`
- Text color: `#ffffff`
- Font size: `0.875rem`
- Padding: `0.5rem`
- Border radius: `0.25rem`
- Positioned directly over mouse cursor
- Format: `{value} {unit}`

**Clear Selection Button**
- Position: Absolute, bottom right corner (1rem from edges)
- Background: Same as `legend_background` prop
- Border: `1px solid #dee2e6`
- Border radius: `0.25rem`
- Padding: `0.5rem 1rem`
- Font size: `0.875rem`
- Color: `#212529`
- Cursor: `pointer`
- Hover: `rgba(13, 110, 253, 0.1)` background tint
- Transition: `all 0.15s ease-in-out`

**MapLegend Position**
- Position: Absolute, top right corner (1rem from edges)
- Z-index: 1000 (above map)

**Typography**
- Font family: `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif`

**Accessibility**
- Keyboard navigation for cell selection
- ARIA labels for interactive elements
- Focus states on selectable cells
- Screen reader support for map legend and values




