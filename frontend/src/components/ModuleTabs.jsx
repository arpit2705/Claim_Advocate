import React from 'react';

export default function ModuleTabs({ activeTab, onTabChange }) {
  return (
    <div className="flex justify-center">
      <div className="relative inline-flex bg-white rounded-full p-2 border border-gray-200 shadow-sm">
        {/* Sliding indicator */}
        <div
          className="absolute top-2 bottom-2 rounded-full bg-navy shadow-md transition-all duration-500 ease-[cubic-bezier(0.16,1,0.3,1)]"
          style={{
            left: activeTab === 'readiness' ? '8px' : '50%',
            width: 'calc(50% - 8px)',
          }}
        />

        <button
          onClick={() => onTabChange('readiness')}
          className={`relative z-10 px-8 sm:px-12 py-4 rounded-full text-sm sm:text-base font-bold transition-colors duration-300 ${
            activeTab === 'readiness' ? 'text-white' : 'text-navy/60 hover:text-navy'
          }`}
        >
          <span className="flex items-center gap-2">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <path d="M9 15l2 2 4-4"/>
            </svg>
            Before You Submit
          </span>
        </button>

        <button
          onClick={() => onTabChange('adjudication')}
          className={`relative z-10 px-8 sm:px-12 py-4 rounded-full text-sm sm:text-base font-bold transition-colors duration-300 ${
            activeTab === 'adjudication' ? 'text-white' : 'text-navy/60 hover:text-navy'
          }`}
        >
          <span className="flex items-center gap-2">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2L3 7v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7l-9-5z"/>
            </svg>
            If You're Rejected
          </span>
        </button>
      </div>
    </div>
  );
}
