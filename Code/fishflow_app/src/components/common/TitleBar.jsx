import React from 'react';
import './TitleBar.css';

/**
 * TitleBar - Displays report title and navigation buttons.
 *
 * Shows scenario name, report type, and provides navigation controls
 * for returning to selection page or home.
 *
 * @param {Object} props
 * @param {string} props.scenarioName - Name of the scenario being displayed
 * @param {string} props.reportType - Type of report (e.g., "Depth Occupancy Report")
 * @param {Function} props.onBack - Callback for navigating back to report selection
 * @param {Function} props.onHome - Callback for navigating to home page
 * @returns {JSX.Element}
 *
 * @example
 * <TitleBar
 *   scenarioName="Chinook 2022"
 *   reportType="Depth Occupancy Report"
 *   onBack={handleBack}
 *   onHome={handleHome}
 * />
 */
const TitleBar = ({ scenarioName, reportType, onBack, onHome }) => {
  return (
    <header className="title-bar">
      <div className="title-bar__content">
        <div className="title-bar__text">
          <div className="title-bar__report-type">{reportType}</div>
          <div className="title-bar__scenario-name">{scenarioName}</div>
        </div>
        <div className="title-bar__buttons">
          <button
            className="title-bar__button"
            onClick={onBack}
            aria-label="Back to Selection"
          >
            Back to Selection
          </button>
          <button
            className="title-bar__button"
            onClick={onHome}
            aria-label="Home"
          >
            Home
          </button>
        </div>
      </div>
    </header>
  );
};

export default TitleBar;
