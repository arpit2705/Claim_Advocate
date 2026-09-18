import React, { useState } from 'react';

export default function EvidenceTrace({ matchedClause, referencedFacts }) {
  const [isOpen, setIsOpen] = useState(false);

  if (!matchedClause && (!referencedFacts || referencedFacts.length === 0)) return null;

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
            {/* Clause Node */}
            {matchedClause && (
              <div className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active animate-trace-reveal">
                <div className="flex items-center justify-center w-10 h-10 rounded-full border-4 border-white bg-blue-100 text-blue-600 shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 shadow-sm z-10">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
                </div>
                <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] p-4 rounded-xl bg-gray-50 border border-gray-100 shadow-sm">
                  <span className="text-xs font-bold text-blue-600 uppercase tracking-wider mb-1 block">Matched Clause: {matchedClause.clause_id}</span>
                  <p className="text-sm text-gray-700 leading-relaxed">{matchedClause.raw_text}</p>
                </div>
              </div>
            )}
            
            {/* Facts Nodes */}
            {referencedFacts?.map((fact, index) => (
              <div key={index} className="relative flex items-center justify-between md:justify-normal md:even:flex-row-reverse group is-active animate-trace-reveal" style={{animationDelay: `${(index + 1) * 0.15}s`}}>
                <div className="flex items-center justify-center w-10 h-10 rounded-full border-4 border-white bg-green-100 text-green-600 shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 shadow-sm z-10">
                   <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/></svg>
                </div>
                <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] p-4 rounded-xl bg-gray-50 border border-gray-100 shadow-sm">
                  <div className="flex justify-between items-start mb-1">
                    <span className="text-xs font-bold text-green-600 uppercase tracking-wider block">Extracted Fact</span>
                    <span className="text-[10px] bg-gray-200 text-gray-600 px-2 py-0.5 rounded-full">{fact.source_document} {fact.page ? `(p. ${fact.page})` : ''}</span>
                  </div>
                  <p className="text-sm text-gray-700 leading-relaxed"><span className="font-semibold">{fact.field}:</span> {fact.value}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
