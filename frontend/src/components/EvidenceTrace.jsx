import React, { useState } from 'react';

export default function EvidenceTrace({ passes }) {
  const [isOpen, setIsOpen] = useState(false);

  if (!passes || passes.length === 0) return null;

  return (
    <div className="mt-8 border border-gray-200 rounded-2xl overflow-hidden bg-white">
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-5 bg-gray-50 hover:bg-gray-100 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-accent-2/20 flex items-center justify-center text-accent-2">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          </div>
          <span className="font-semibold text-navy">Why did Claim Advocate reach this result?</span>
        </div>
        <svg 
          className={`w-5 h-5 text-gray-500 transition-transform ${isOpen ? 'rotate-180' : ''}`} 
          fill="none" stroke="currentColor" viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <div className="p-6 border-t border-gray-200">
          <div className="space-y-4 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-gray-300 before:to-transparent">
            {passes.map((pass, index) => (
              <div key={index} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active animate-trace-reveal" style={{animationDelay: `${index * 0.15}s`}}>
                <div className="flex items-center justify-center w-10 h-10 rounded-full border-4 border-white bg-accent-2/10 text-accent-2 shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 shadow-sm z-10">
                  <span className="text-xs font-bold">{index + 1}</span>
                </div>
                <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] p-4 rounded-xl bg-gray-50 border border-gray-100 shadow-sm">
                  <p className="text-sm text-gray-700 leading-relaxed">{pass}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
