import React, { useState, useEffect } from 'react';

export default function ReadinessScore({ score, verification_status }) {
  const [animatedScore, setAnimatedScore] = useState(0);
  const radius = 70;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (animatedScore / 100) * circumference;

  useEffect(() => {
    const timer = setTimeout(() => setAnimatedScore(score), 200);
    return () => clearTimeout(timer);
  }, [score]);

  const getColor = () => {
    if (score >= 80) return { stroke: '#67CFC3', bg: 'bg-[#67CFC3]/10', text: 'text-[#67CFC3]', label: 'Strong Readiness' };
    if (score >= 60) return { stroke: '#5AAFD5', bg: 'bg-[#5AAFD5]/10', text: 'text-[#5AAFD5]', label: 'Moderate Readiness' };
    return { stroke: '#ef4444', bg: 'bg-red-50', text: 'text-red-700', label: 'Needs Attention' };
  };

  const color = getColor();

  // Verification Badge logic
  let vsIcon = null;
  let vsText = "";
  let vsStyles = "";

  if (verification_status === "FULLY_VERIFIED") {
    vsText = "Fully Verified";
    vsStyles = "bg-green-50 border-green-200 text-green-800";
    vsIcon = <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>;
  } else if (verification_status === "PARTIALLY_VERIFIED") {
    vsText = "Partially Verified";
    vsStyles = "bg-amber-50 border-amber-200 text-amber-800";
    vsIcon = <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>;
  } else {
    // REQUIRES_REVIEW
    vsText = "Requires Review";
    vsStyles = "bg-red-50 border-red-200 text-red-800";
    vsIcon = <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>;
  }

  return (
    <div className="flex flex-col items-center animate-scale-in">
      <div className="relative w-48 h-48 mb-4">
        <svg className="w-48 h-48 transform -rotate-90" viewBox="0 0 160 160">
          <circle cx="80" cy="80" r={radius} fill="none" stroke="#e5e7eb" strokeWidth="10" />
          <circle
            cx="80" cy="80" r={radius} fill="none"
            stroke={color.stroke} strokeWidth="10"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            style={{ transition: 'stroke-dashoffset 1.5s ease-out' }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-5xl font-bold text-navy">{Math.round(animatedScore)}</span>
          <span className="text-gray-400 text-sm font-medium">/100</span>
        </div>
      </div>
      <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full ${color.bg}`}>
        <div className={`w-2 h-2 rounded-full`} style={{ backgroundColor: color.stroke }} />
        <span className={`text-sm font-semibold ${color.text}`}>{color.label}</span>
      </div>
      
      {verification_status && (
        <div className={`mt-4 border rounded-xl px-4 py-3 max-w-sm text-center ${vsStyles}`}>
          <p className="text-sm font-semibold flex items-center justify-center gap-1">
            {vsIcon}
            {vsText}
          </p>
          <p className="text-xs opacity-80 mt-1">
            {verification_status === "FULLY_VERIFIED" 
              ? "All critical facts grounded in uploaded documents." 
              : verification_status === "PARTIALLY_VERIFIED"
                ? "Some required evidence is missing or cannot be verified."
                : "Conflicts or critical issues require manual review."}
          </p>
        </div>
      )}
    </div>
  );
}
