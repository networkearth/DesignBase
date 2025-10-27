# FishFlow App

A React application that displays interactive visualizations of FishFlow behavioral model predictions. Users can explore depth occupancy reports to plan harvest operations and minimize bycatch risk.

## Features

- **Interactive Map Visualization**: View depth occupancy predictions across geographical cells
- **Time-Based Filtering**: Filter data by months and hours to match harvest windows
- **Cell Drill-Down**: Click cells to view detailed occupancy timelines with confidence intervals
- **URL State Management**: Share specific views via URL parameters
- **Responsive Design**: Optimized layout for various screen sizes

## Technology Stack

- **React** 18.2.0+ - UI framework
- **React Router** 6.20.0+ - Client-side routing
- **react-leaflet** 4.2.1+ - Interactive maps
- **leaflet** 1.9.4 - Map library
- **recharts** 2.10.0+ - Data visualization
- **d3** 7.8.5+ - Data manipulation and color interpolation
- **axios** 1.6.0+ - HTTP client
- **date-fns** 2.30.0+ - Date formatting

## Installation

### Option 1: Install from existing project

```bash
cd fishflow_app
npm install
```

### Option 2: Initialize from scratch

```bash
npx create-react-app fishflow_app
cd fishflow_app
npm install react-router-dom react-leaflet leaflet recharts d3 axios date-fns
```

Then copy the source files from this repository into the appropriate directories.

## Configuration

The app uses environment variables to configure API endpoints:

### Environment Variables

Create a `.env` file in the project root:

```bash
# Mode: DEV or PROD (case-sensitive)
REACT_APP_FISHFLOW_MODE=DEV

# Production API URL (only used when REACT_APP_FISHFLOW_MODE=PROD)
REACT_APP_API_URL=https://networkearth.io
```

**Modes:**
- `DEV`: Uses `http://localhost:8000` as the API base URL
- `PROD`: Uses the URL specified in `REACT_APP_API_URL`

## Development

```bash
# Start development server
npm start

# Runs on http://localhost:3000
# Hot-reloading enabled for rapid development
```

## Production Build

```bash
# Create optimized production build
npm run build

# Output in build/ directory
# Ready for deployment to static hosting
```

## Testing

```bash
# Run test suite
npm test

# Runs in interactive watch mode
```

## Project Structure

```
fishflow_app/
├── package.json
├── .env
├── README.md
├── public/
│   └── index.html
├── src/
│   ├── App.js                    # Main app with routing
│   ├── index.js                  # Entry point
│   ├── index.css                 # Global styles
│   ├── components/
│   │   ├── common/
│   │   │   ├── CheckBoxPicker.jsx
│   │   │   ├── CheckBoxPicker.css
│   │   │   ├── HourPicker.jsx
│   │   │   ├── MonthPicker.jsx
│   │   │   ├── TitleBar.jsx
│   │   │   └── TitleBar.css
│   │   ├── mapping/
│   │   │   ├── MapLegend.jsx
│   │   │   ├── MapLegend.css
│   │   │   ├── CellMap.jsx
│   │   │   └── CellMap.css
│   │   └── plotting/
│   │       ├── ContourDateGraph.jsx
│   │       └── ContourDateGraph.css
│   ├── pages/
│   │   ├── DepthOccupancyReport.jsx
│   │   ├── DepthOccupancyReport.css
│   │   └── depthOccupancyHelpers.js
│   └── functions/
│       └── coloring.js
└── tests/
```

## Routes

- `/` - Redirects to `/depth_occupancy/example`
- `/depth_occupancy/:scenario_id` - Depth occupancy report page
- `*` - Catch-all redirects to `/depth_occupancy/example`

### URL Parameters

Reports support URL parameters for state sharing:

```
/depth_occupancy/{scenario_id}?months=1,2,3,4&hours=6,7,8,9,10,11,12,13,14,15,16,17,18&cell_id=132
```

- `months`: Comma-separated month numbers (1-12)
- `hours`: Comma-separated hour numbers (0-23)
- `cell_id`: Selected cell identifier

## API Integration

The app consumes the FishFlow API with the following endpoints:

- `/v1/depth/scenario/{scenario_id}/scenario` - Scenario metadata
- `/v1/depth/scenario/{scenario_id}/geometries` - Cell geometries (GeoJSON)
- `/v1/depth/scenario/{scenario_id}/cell_depths` - Maximum depth per cell
- `/v1/depth/scenario/{scenario_id}/timestamps` - Temporal data points
- `/v1/depth/scenario/{scenario_id}/minimums` - Minimum occupancy values
- `/v1/depth/scenario/{scenario_id}/occupancy` - Detailed occupancy predictions

## Usage

### Basic Usage

1. Start the development server: `npm start`
2. Navigate to `http://localhost:3000`
3. The app will load the example scenario by default
4. Use the month and hour pickers to filter harvest windows
5. Click cells on the map to view detailed occupancy timelines
6. Share views by copying the URL

### Customization

To connect to a different API:

1. Update `.env` to set `REACT_APP_FISHFLOW_MODE=PROD`
2. Set `REACT_APP_API_URL` to your API endpoint
3. Restart the development server

## Key Components

### DepthOccupancyReport

Main page component that orchestrates the visualization. Manages state for:
- Selected months, hours, and cells
- Loaded data (scenario, geometries, timestamps, occupancy)
- Filtered and derived data
- Loading and error states

### CellMap

Interactive map displaying colored cells based on occupancy values. Features:
- Color interpolation from low to high values
- Cell selection with visual feedback
- Hover tooltips showing values
- Dynamic legend generation

### ContourDateGraph

Timeline visualization showing multiple forecast lines with confidence intervals. Features:
- Support-based opacity for confidence visualization
- Highlighted time segments for selected hours
- Interactive tooltips with line-specific data

### CheckBoxPicker

Reusable multi-select component with customizable layout and styling. Used by:
- MonthPicker (months 1-12)
- HourPicker (hours 0-23)

## Design Decisions

### Assumptions Made

1. **Default Cell Selection**: When no cell is specified in the URL, the first cell from the geometries array is selected
2. **Depth Bin Selection**: Only the maximum depth bin per cell is used, as specified in the design
3. **Color Scale**: Uses 0th, 25th, 50th, 75th, and 100th percentiles for the map legend
4. **Error Handling**: Displays user-friendly error messages with retry buttons for failed API requests
5. **Loading States**: Shows spinners during data loading to provide feedback
6. **Empty States**: Displays helpful placeholder text when no cell is selected

### Libraries Chosen

- **D3**: Industry standard for data visualization and color interpolation
- **Recharts**: React-friendly charting library with good TypeScript support
- **react-leaflet**: Well-maintained React wrapper for Leaflet maps
- **axios**: Popular HTTP client with interceptor support for future enhancements
- **date-fns**: Lightweight alternative to moment.js for date formatting

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## License

Copyright © 2024 Network Earth. All rights reserved.

## Support

For issues or questions, please contact the development team or open an issue in the project repository.
