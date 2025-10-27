import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import DepthOccupancyReport from './pages/DepthOccupancyReport';

/**
 * App - Main application component with routing.
 *
 * Sets up React Router with the following routes:
 * - / : Redirects to /depth_occupancy/example
 * - /depth_occupancy/:scenario_id : Displays the depth occupancy report
 * - * : Catch-all redirects to /depth_occupancy/example
 */
function App() {
  return (
    <Router>
      <Routes>
        {/* Root route - redirect to example scenario */}
        <Route path="/" element={<Navigate to="/depth_occupancy/example" replace />} />

        {/* Depth occupancy report route */}
        <Route path="/depth_occupancy/:scenario_id" element={<DepthOccupancyReport />} />

        {/* Catch-all route - redirect to example scenario */}
        <Route path="*" element={<Navigate to="/depth_occupancy/example" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
