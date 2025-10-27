## `FishFlow App!`

### Interfaces

```
npm run
```

### Use Cases

A `React` app that displays `FishFlow` reports.

### Build

Just your standard `React` app that indexes at `App.js` in `src`

For now there's not much to it as we're in development.

#### Dependencies

- `App.js`

## `App.js`

For now, as we're just in development this is super simple. We will just load a dev scenario straight into `../DepthOccupancyReport.md:DepthOccupancyReport` and display nothing but that component. 

### Build

#### Placement

```
fishflow
|
+-- frontend
|   |
|   +-- src
|   |   |
|   |   +-- App.js <--
```


## React Router Configuration

### Interfaces

The app uses React Router for URL-based state management.

### Use Cases

Enables URL-based state sharing for the depth occupancy report, allowing users to share specific views (selected months, hours, and cells) via URL.

### Build

Install React Router:
```bash
npm install react-router-dom
```

In `App.js`, wrap the application with `BrowserRouter` and define routes:

```jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import DepthOccupancyReport from './pages/DepthOccupancyReport';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/depth_occupancy/:scenario_id" element={<DepthOccupancyReport />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
```

### URL Parameter Format

The DepthOccupancyReport component should read and write URL parameters in this format:
```
/depth_occupancy/{scenario_id}?months=1,2,3,4&hours=6,7,8,9,10,11,12,13,14,15,16,17,18&cell_id=132
```

- `months`: Comma-separated list of month numbers (1-12)
- `hours`: Comma-separated list of hour numbers (0-23)
- `cell_id`: Single cell ID number

### URL Synchronization Behavior

- URL parameters should update **immediately** when user makes selections
- URL changes do **not** need to create browser history entries (use `replace` instead of `push`)
- On initial load, URL parameters take precedence over defaults
- If URL parameters are missing, use defaults: months=1,2,3,4, hours=6-18, cell_id=(first cell in geometries)

### Constraints

N/A

## Environment Configuration

### Interfaces

Environment variables to configure the application behavior.

### Use Cases

Allows the application to determine which backend API URL to use (development vs production).

### Build

Create a `.env` file in the frontend root directory:

```
REACT_APP_FISHFLOW_MODE=dev
```

- `REACT_APP_FISHFLOW_MODE=dev`: Use `http://localhost:3000` as the API base URL
- `REACT_APP_FISHFLOW_MODE=prod`: Use production API URL (to be specified by whoever deploys the app)

Access in code:
```jsx
const apiBaseUrl = process.env.REACT_APP_FISHFLOW_MODE === 'dev' 
  ? 'http://localhost:3000' 
  : process.env.REACT_APP_API_URL;
```

### Placement

```
fishflow
|
+-- frontend
|   |
|   +-- .env <--
```

### Constraints

- Must use `REACT_APP_` prefix for Create React App to expose the variable
- Environment variable set by whoever runs/deploys the application
