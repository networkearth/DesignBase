# Package Configuration

## `package.json`

### Interfaces

N/A

### Use Cases

Defines the dependencies and scripts for the FishFlow React application.

### Build

Create this `package.json` file in the frontend root directory:

```json
{
  "name": "fishflow-frontend",
  "version": "0.1.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "react-leaflet": "^4.2.1",
    "leaflet": "^1.9.4",
    "recharts": "^2.10.0",
    "d3": "^7.8.5",
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "react-scripts": "5.0.1"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": [
      "react-app"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }
}
```

### Installation

Initialize the project:
```bash
npx create-react-app fishflow-frontend
cd fishflow-frontend
npm install react-router-dom react-leaflet leaflet recharts d3 axios
```

Or use the package.json above and run:
```bash
npm install
```

### Running the Application

Development server:
```bash
npm start
```

Production build:
```bash
npm run build
```

### Placement

```
fishflow
|
+-- frontend
|   |
|   +-- package.json <--
```

### Constraints

**Dependency Version Notes:**
- React 18.2.0+ for latest features and performance
- React Router 6.20.0+ for modern routing API
- react-leaflet 4.2.1+ compatible with Leaflet 1.9.4
- recharts 2.10.0+ for stable charting API
- d3 7.8.5+ for color interpolation
- axios 1.6.0+ for HTTP requests

These versions are tested to work together. Implementer may use newer minor/patch versions if compatible.
