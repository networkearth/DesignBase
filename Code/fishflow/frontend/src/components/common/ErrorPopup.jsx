import React from 'react';
import './ErrorPopup.css';

/**
 * ErrorPopup Component
 *
 * Displays error messages with retry and close options.
 *
 * @param {string} message - Main error message to display
 * @param {string} details - Technical details about the error (optional)
 * @param {Function} onRetry - Callback function to retry the failed operation
 * @param {Function} onClose - Callback function to close the error popup
 */
const ErrorPopup = ({
  message,
  details,
  onRetry,
  onClose
}) => {
  return (
    <div className="error-popup__overlay" onClick={onClose}>
      <div className="error-popup__box" onClick={(e) => e.stopPropagation()}>
        <div className="error-popup__title">{message}</div>
        {details && (
          <div className="error-popup__details">{details}</div>
        )}
        <div className="error-popup__actions">
          {onRetry && (
            <button
              className="error-popup__button error-popup__button--retry"
              onClick={onRetry}
            >
              Retry
            </button>
          )}
          <button
            className="error-popup__button error-popup__button--close"
            onClick={onClose}
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default ErrorPopup;
