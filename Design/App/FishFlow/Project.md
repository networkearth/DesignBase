## Summary
A `React` application that displays interactive visualizations of `FishFlow` behavioral model predictions. Users can explore depth occupancy reports to plan harvest operations and minimize bycatch risk.

```bash
npm start
```

## Roots
```bash
http://localhost:3000 (development)
https://networkearth.io (production)
```

## Config

#### Environment Variables
- `REACT_APP_FISHFLOW_MODE` - `DEV` or `PROD` (case-sensitive), determines which API URL to use
- `REACT_APP_API_URL` - Production API URL (only used when `REACT_APP_FISHFLOW_MODE=PROD`) (for `DEV` `http://localhost:8000` is used for the API URL)

#### Example `.env`
```
REACT_APP_FISHFLOW_MODE=DEV
REACT_APP_API_URL=https://networkearth.io
```

## Structure
```bash
fishflow_app/
+-- package.json
+-- .env
+-- public/
|   +-- index.html
+-- src/
|   +-- App.js
|   +-- index.js
|   +-- components/
|   |   +-- common/
|   |   |   +-- CheckBoxPicker.jsx
|   |   |   +-- HourPicker.jsx
|   |   |   +-- MonthPicker.jsx
|   |   |   +-- TitleBar.jsx
|   |   +-- mapping/
|   |   |   +-- MapLegend.jsx
|   |   |   +-- CellMap.jsx
|   |   +-- plotting/
|   |   |   +-- ContourDateGraph.jsx
|   +-- pages/
|   |   +-- DepthOccupancyReport.jsx
|   +-- functions/
|   |   +-- coloring.js
+-- tests/
```

## Stack
```bash
React 18.2.0+
React Router 6.20.0+
react-leaflet 4.2.1+
leaflet 1.9.4
recharts 2.10.0+
d3 7.8.5+
axios 1.6.0+
react-scripts 5.0.1
```

## Installation
```bash
npm install
```

Or initialize from scratch:
```bash
npx create-react-app fishflow-frontend
cd fishflow-frontend
npm install react-router-dom react-leaflet leaflet recharts d3 axios
```

## Development
```bash
npm start          # Start development server on http://localhost:3000
npm test           # Run tests
npm run build      # Create production build
```

## Tests
Should be selected and added by the LLM.

## Routing
The app uses React Router for URL-based state management:

**Routes:**
- `/depth_occupancy/:scenario_id` - Depth occupancy report page with URL parameters for sharing views

**URL Parameter Format:**
```
/depth_occupancy/{scenario_id}?months=1,2,3,4&hours=6,7,8,9,10,11,12,13,14,15,16,17,18&cell_id=132
```

Parameters synchronize with user selections using `replace: true` to avoid polluting browser history.

## API Integration
The app consumes the `FishFlow` (`../../API/FishFlow/`) API to load report data:

**Endpoints Used:**
- `/v1/depth/scenario/{scenario_id}/scenario` - Scenario metadata
- `/v1/depth/scenario/{scenario_id}/geometries` - Cell geometries (GeoJSON)
- `/v1/depth/scenario/{scenario_id}/cell_depths` - Maximum depth per cell
- `/v1/depth/scenario/{scenario_id}/timestamps` - Temporal data points
- `/v1/depth/scenario/{scenario_id}/minimums` - Minimum occupancy values
- `/v1/depth/scenario/{scenario_id}/occupancy` - Detailed occupancy predictions

**Environment-Based URL Resolution:**
```jsx
const apiBaseUrl = process.env.REACT_APP_FISHFLOW_MODE === 'DEV'
  ? 'http://localhost:8000'
  : process.env.REACT_APP_API_URL;
```

## Design Philosophy

## Further Designs
- `Pages/` - Page-level components
- `Components/` - Reusable UI components
