import React, { useState, useEffect } from 'react';

export default function ReadinessScore({ score, grounded }) {
  const [animatedScore, setAnimatedScore] = useState(0);
  const radius = 70;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (animatedScore / 100) * circumference;

  useEffect(() => {
    const timer = setTimeout(() => setAnimatedScore(score), 200);
    return () => clearTimeout(timer);
  }, [score]);

  const getColor = () => {
    if (score >= 80) return { stroke: '#67CFC3', bg: 'bg-[#67CFC3]/10', text: 'text-[#67CFC3]', label: 'Strong Readiness' }; // accent-3
    if (score >= 60) return { stroke: '#5AAFD5', bg: 'bg-[#5AAFD5]/10', text: 'text-[#5AAFD5]', label: 'Moderate Readiness' }; // accent-1
    return { stroke: '#ef4444', bg: 'bg-red-50', text: 'text-red-700', label: 'Needs Attention' };
  };

  const color = getColor();

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
      {!grounded && (
        <div className="mt-4 bg-amber-50 border border-amber-200 rounded-xl px-4 py-3 max-w-sm text-center">
          <p className="text-amber-800 text-sm font-semibold mb-1">Unable to Fully Verify</p>
          <p className="text-amber-600 text-xs">
            The available evidence could not fully ground this result. This score should not be treated as fully verified.
          </p>
        </div>
      )}
    </div>
  );
}
