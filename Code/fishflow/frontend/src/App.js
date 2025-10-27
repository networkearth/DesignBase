import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import DepthOccupancyReport from './pages/DepthOccupancyReport';

/**
 * Main App Component
 *
 * Sets up React Router and defines routes for the FishFlow application.
 * During development, we load directly into the DepthOccupancyReport component.
 */
function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/depth_occupancy/:scenario_id" element={<DepthOccupancyReport />} />
        {/* Default route also loads depth occupancy report with a default scenario */}
        <Route path="/" element={<DepthOccupancyReport />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
