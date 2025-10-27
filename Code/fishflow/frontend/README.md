# FishFlow Frontend

A React application for displaying FishFlow depth occupancy reports, enabling harvesters to explore depth occupancy predictions during harvest windows to minimize bycatch risk.

## Features

- **Interactive Map Visualization**: View minimum likelihood of occupancy across geographical cells
- **Time-based Filtering**: Filter data by months and hours to match harvest windows
- **Detailed Timeline View**: Drill down into specific cells to see full occupancy predictions over time
- **URL-based State Sharing**: Share specific views via URL parameters
- **Confidence Visualization**: Display multiple model predictions with support values

## Installation

### Prerequisites

- Node.js (v14 or higher)
- npm (v6 or higher)

### Setup

1. Navigate to the frontend directory:
```bash
cd fishflow/frontend
```

2. Install dependencies:
```bash
npm install
```

3. Configure environment variables:

Create or modify the `.env` file in the frontend root directory:

```
REACT_APP_FISHFLOW_MODE=dev
```

- For development: `REACT_APP_FISHFLOW_MODE=dev` (uses `http://localhost:3000` as API base URL)
- For production: `REACT_APP_FISHFLOW_MODE=prod` and set `REACT_APP_API_URL` to your production API URL

## Usage

### Development Server

Start the development server:

```bash
npm start
```

The application will open at [http://localhost:3001](http://localhost:3001) (or next available port).

### Production Build

Build the application for production:

```bash
npm run build
```

The optimized build will be created in the `build/` directory.

### Running Tests

Run the test suite:

```bash
npm test
```

## Application Structure

```
fishflow/frontend/
├── public/
│   └── index.html           # HTML template
├── src/
│   ├── components/
│   │   ├── common/          # Reusable UI components
│   │   │   ├── CheckBoxPicker.jsx
│   │   │   ├── MonthPicker.jsx
│   │   │   ├── HourPicker.jsx
│   │   │   ├── TitleBar.jsx
│   │   │   └── ErrorPopup.jsx
│   │   ├── mapping/         # Map-related components
│   │   │   ├── MapLegend.js
│   │   │   └── CellMap.js
│   │   └── plotting/        # Chart components
│   │       └── ContourDateGraph.jsx
│   ├── functions/
│   │   └── common/
│   │       └── coloring.js  # Color interpolation utilities
│   ├── pages/
│   │   └── DepthOccupancyReport.jsx  # Main report page
│   ├── App.js               # React Router configuration
│   ├── index.js             # Application entry point
│   └── index.css            # Global styles
├── package.json
├── .env                     # Environment configuration
└── README.md
```

## Component Overview

### Pages

- **DepthOccupancyReport**: Main report view with map, timeline, and interactive filters

### Common Components

- **CheckBoxPicker**: Customizable multi-select checkbox grid
- **MonthPicker**: Month selection wrapper around CheckBoxPicker
- **HourPicker**: Hour selection wrapper around CheckBoxPicker
- **TitleBar**: Application header with navigation
- **ErrorPopup**: Error display with retry functionality

### Mapping Components

- **CellMap**: Interactive Leaflet map with colored cells and selection
- **MapLegend**: Color scale legend for map visualization

### Plotting Components

- **ContourDateGraph**: Multi-line time series chart with highlighted regions

## API Integration

The application expects a backend API with the following endpoints:

### Global Data Endpoints

- `GET /v1/depth/scenario/{scenario_id}/scenario` - Scenario metadata
- `GET /v1/depth/scenario/{scenario_id}/geometries` - GeoJSON cell geometries
- `GET /v1/depth/scenario/{scenario_id}/cell_depths` - Maximum depth per cell
- `GET /v1/depth/scenario/{scenario_id}/timestamps` - Timestamp array
- `GET /v1/depth/scenario/{scenario_id}/minimums` - Minimum occupancy values

### Occupancy Data Endpoint

- `GET /v1/depth/scenario/{scenario_id}/occupancy?cell_id={cell_id}&depth_bin={depth_bin}` - Occupancy predictions for a specific cell

## URL Parameters

The application uses URL parameters for state sharing:

```
/depth_occupancy/{scenario_id}?months=1,2,3,4&hours=6,7,8,9,10,11,12,13,14,15,16,17,18&cell_id=132
```

- `months`: Comma-separated month numbers (1-12)
- `hours`: Comma-separated hour numbers (0-23)
- `cell_id`: Selected cell ID

URL updates happen immediately on user interaction without creating browser history entries.

## Styling

The application uses Bootstrap-inspired styling conventions:

- **Colors**:
  - Primary: `#0d6efd`
  - Border: `#dee2e6`
  - Text: `#212529`
  - Background: `#ffffff`

- **Typography**: System font stack for native appearance across platforms

- **Spacing**: Consistent rem-based spacing scale

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Implementation Notes

### Design Decisions

1. **Color Interpolation**: Uses D3 for smooth color gradients based on data values
2. **Map Library**: Leaflet via react-leaflet for robust mapping capabilities
3. **Charting**: Recharts for declarative, React-friendly charts
4. **State Management**: React hooks with URL synchronization for shareable state
5. **Error Handling**: Graceful degradation with user-friendly error messages

### Assumptions

- Timestamps from API are in `YYYY-MM-DD HH:MM:SS` format (UTC)
- All occupancy values are between 0 and 1
- Cell IDs in GeoJSON match keys in data objects
- Maximum depth bin per cell is used for occupancy queries

## Troubleshooting

### Map Not Displaying

Ensure Leaflet CSS is imported. The application imports it in `CellMap.js`:

```javascript
import 'leaflet/dist/leaflet.css';
```

### API Connection Issues

1. Check that `.env` has correct `REACT_APP_FISHFLOW_MODE` setting
2. Verify backend API is running on expected port (3000 for dev mode)
3. Check browser console for CORS errors

### Component Not Rendering

1. Check browser console for errors
2. Verify all required props are being passed
3. Ensure data format matches expected structure

## Contributing

When adding new features:

1. Follow existing component structure and naming conventions
2. Add PropTypes or TypeScript types for props
3. Include CSS file with component-specific styles
4. Update this README if adding new major features

## License

[To be specified by project owner]
