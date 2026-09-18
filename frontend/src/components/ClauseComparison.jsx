import React from 'react';

export default function ClauseComparison({ matchedClauseId, matchedClauseText, insurerReason, mismatchExplanation }) {
  return (
    <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-sm animate-fade-in-up mt-8">
      <div className="p-4 bg-navy text-white flex justify-between items-center">
        <h3 className="font-bold">Policy Clause Comparison</h3>
      </div>
      
      <div className="grid md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-gray-200">
        <div className="p-6">
          <div className="flex items-center gap-2 mb-3">
            <span className="uppercase text-xs font-bold text-gray-500 tracking-wider">Insurer's Stated Reason</span>
          </div>
          <div className="bg-gray-50 rounded-xl p-4 text-gray-700 text-sm leading-relaxed italic border-l-4 border-gray-300">
            "{insurerReason}"
          </div>
        </div>
        
        <div className="p-6">
          <div className="flex items-center justify-between mb-3">
            <span className="uppercase text-xs font-bold text-gray-500 tracking-wider">Matched Policy Clause</span>
            {matchedClauseId && (
              <span className="text-xs font-mono bg-primary/10 text-primary-dark px-2 py-1 rounded">
                {matchedClauseId}
              </span>
            )}
          </div>
          <div className="bg-primary/5 rounded-xl p-4 text-gray-800 text-sm leading-relaxed border-l-4 border-primary">
            {matchedClauseText || "Clause text not provided."}
          </div>
        </div>
      </div>
      
      {mismatchExplanation && (
        <div className="p-6 border-t border-gray-100 bg-gray-50/50">
          <h4 className="text-sm font-bold text-navy mb-2">Claim Advocate Analysis</h4>
          <p className="text-gray-700 text-sm leading-relaxed">
            {mismatchExplanation}
          </p>
        </div>
      )}
    </div>
  );
}
