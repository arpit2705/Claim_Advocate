import React from 'react';

export default function ErrorAlert({ message, onRetry }) {
  return (
    <div className="bg-red-50 border border-red-200 rounded-2xl p-6 animate-fade-in">
      <div className="flex items-start gap-4">
        <div className="w-10 h-10 bg-red-100 rounded-xl flex items-center justify-center flex-shrink-0">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
        </div>
        <div className="flex-1">
          <h4 className="text-red-800 font-semibold mb-1">Analysis Failed</h4>
          <p className="text-red-600 text-sm">
            {message || "We couldn't complete the analysis. Please check the uploaded documents and try again."}
          </p>
          {onRetry && (
            <button
              onClick={onRetry}
              className="mt-3 text-sm font-semibold text-red-700 hover:text-red-800 underline underline-offset-2"
            >
              Try Again
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
