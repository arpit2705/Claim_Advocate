import React, { useState } from 'react';

const HUMAN_NAMES = {
  "waiting_period_check": "Waiting Period",
  "sub_limit_check": "Room Rent Limit",
  "deadline_check": "Claim Deadline",
  "coverage_period_check": "Coverage Period",
  "chronology_check": "Date Consistency"
};

const STATUS_LABELS = {
  "PASS": "Passed",
  "FAIL": "Failed",
  "UNKNOWN": "Cannot verify",
  "NOT_APPLICABLE": "Not applicable"
};

export default function RequirementCheck({ rule, index }) {
  const [expanded, setExpanded] = useState(false);
  const status = rule.status; // "PASS", "FAIL", "UNKNOWN", "NOT_APPLICABLE"
  
  let borderColor = 'border-gray-200';
  let bgColor = 'bg-gray-50/50';
  let iconBg = 'bg-gray-100';
  let textColorTitle = 'text-gray-800';
  let textColorDesc = 'text-gray-600';
  let Icon = null;

  if (status === 'PASS') {
    borderColor = 'border-green-200';
    bgColor = 'bg-green-50/50';
    iconBg = 'bg-green-100';
    textColorTitle = 'text-green-800';
    textColorDesc = 'text-green-700/80';
    Icon = (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#22c55e" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
        <polyline points="20 6 9 17 4 12"/>
      </svg>
    );
  } else if (status === 'FAIL') {
    borderColor = 'border-red-200';
    bgColor = 'bg-red-50/50';
    iconBg = 'bg-red-100';
    textColorTitle = 'text-red-800';
    textColorDesc = 'text-red-700/80';
    Icon = (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
        <line x1="18" y1="6" x2="6" y2="18"/>
        <line x1="6" y1="6" x2="18" y2="18"/>
      </svg>
    );
  } else if (status === 'UNKNOWN') {
    borderColor = 'border-amber-200';
    bgColor = 'bg-amber-50/50';
    iconBg = 'bg-amber-100';
    textColorTitle = 'text-amber-800';
    textColorDesc = 'text-amber-700/80';
    Icon = (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
        <line x1="12" y1="9" x2="12" y2="13"/>
        <line x1="12" y1="17" x2="12.01" y2="17"/>
      </svg>
    );
  } else {
    // NOT_APPLICABLE
    Icon = (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <line x1="5" y1="12" x2="19" y2="12"/>
      </svg>
    );
  }

  const displayName = HUMAN_NAMES[rule.rule_name] || rule.rule_name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());

  // Clean explanation text
  let explanation = rule.explanation;
  if (explanation.startsWith("Cannot evaluate: Insufficient data to evaluate this rule.")) {
    explanation = "Missing required information to verify this requirement.";
  } else if (explanation.startsWith("Cannot evaluate: ")) {
    explanation = explanation.replace("Cannot evaluate: ", "");
  }

  return (
    <div
      className={`border rounded-2xl p-5 card-hover animate-fade-in-up ${borderColor} ${bgColor}`}
      style={{ animationDelay: `${index * 0.1}s` }}
    >
      <div className="flex items-start gap-3">
        <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5 ${iconBg}`}>
          {Icon}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h4 className={`font-bold text-sm ${textColorTitle}`}>
              {displayName}
            </h4>
            <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${iconBg} ${textColorTitle} opacity-80`}>
              {STATUS_LABELS[status] || status}
            </span>
          </div>
          
          <p className={`text-sm leading-relaxed mb-3 ${textColorDesc}`}>
            {explanation}
          </p>
          
          {rule.trace_details && Object.keys(rule.trace_details).length > 0 && (
             <div>
               <button 
                 onClick={() => setExpanded(!expanded)}
                 className="text-xs font-semibold text-primary hover:text-primary-dark flex items-center gap-1 transition-colors"
               >
                 {expanded ? 'Hide Details' : 'Why?'}
                 <svg 
                   width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
                   className={`transform transition-transform ${expanded ? 'rotate-180' : ''}`}
                 >
                   <polyline points="6 9 12 15 18 9"/>
                 </svg>
               </button>
               
               {expanded && (
                 <div className="mt-3 text-xs text-gray-600 bg-white/60 p-3 rounded-xl border border-gray-100">
                   <ul className="space-y-1.5">
                     {Object.entries(rule.trace_details).map(([key, val]) => (
                       <li key={key} className="flex gap-2">
                         <span className="font-medium text-gray-500 capitalize min-w-[120px]">
                           {key.replace(/_/g, ' ')}:
                         </span>
                         <span className="font-semibold text-gray-800 break-words">
                           {val === null ? 'Not found' : String(val)}
                         </span>
                       </li>
                     ))}
                   </ul>
                 </div>
               )}
             </div>
          )}
        </div>
      </div>
    </div>
  );
}
