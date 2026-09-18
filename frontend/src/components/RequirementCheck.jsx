import React from 'react';

export default function RequirementCheck({ rule, index }) {
  const passed = rule.passed;
  return (
    <div
      className={`border rounded-2xl p-5 card-hover animate-fade-in-up ${
        passed
          ? 'border-green-200 bg-green-50/50'
          : 'border-amber-200 bg-amber-50/50'
      }`}
      style={{ animationDelay: `${index * 0.1}s` }}
    >
      <div className="flex items-start gap-3">
        <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5 ${
          passed ? 'bg-green-100' : 'bg-amber-100'
        }`}>
          {passed ? (
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#22c55e" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
          ) : (
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="8" x2="12" y2="12"/>
              <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
          )}
        </div>
        <div className="flex-1 min-w-0">
          <h4 className={`font-semibold text-sm mb-1 ${passed ? 'text-green-800' : 'text-amber-800'}`}>
            {rule.rule_name}
          </h4>
          <p className={`text-sm leading-relaxed ${passed ? 'text-green-700/80' : 'text-amber-700/80'}`}>
            {rule.explanation}
          </p>
        </div>
      </div>
    </div>
  );
}
