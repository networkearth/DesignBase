import React from 'react';
import './TitleBar.css';

/**
 * TitleBar Component
 *
 * Displays the report title with scenario name and navigation buttons.
 *
 * @param {string} scenarioName - Name of the scenario being displayed
 * @param {string} reportType - Type of report (e.g., "Depth Occupancy Report")
 * @param {Function} onBack - Callback for navigating back to report selection
 * @param {Function} onHome - Callback for navigating to home page
 */
const TitleBar = ({
  scenarioName,
  reportType,
  onBack,
  onHome
}) => {
  return (
    <header className="title-bar">
      <div className="title-bar__content">
        <div className="title-bar__text">
          <div className="title-bar__report-type">{reportType}</div>
          <div className="title-bar__scenario-name">{scenarioName}</div>
        </div>
      </div>
      <div className="title-bar__actions">
        {onBack && (
          <button
            className="title-bar__button"
            onClick={onBack}
            aria-label="Back to selection"
          >
            Back to Selection
          </button>
        )}
        {onHome && (
          <button
            className="title-bar__button"
            onClick={onHome}
            aria-label="Go to home"
          >
            Home
          </button>
        )}
      </div>
    </header>
  );
};

export default TitleBar;
