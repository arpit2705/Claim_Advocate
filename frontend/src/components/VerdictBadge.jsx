import React from 'react';

export default function VerdictBadge({ verdict, consistencyScore }) {
  const getVerdictConfig = () => {
    switch (verdict) {
      case 'valid':
        return {
          label: 'VALID REJECTION',
          color: 'bg-green-100 text-green-800 border-green-200',
          icon: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="20 6 9 17 4 12"/></svg>,
          bg: 'bg-green-50',
          stroke: '#22c55e'
        };
      case 'questionable':
        return {
          label: 'QUESTIONABLE',
          color: 'bg-amber-100 text-amber-800 border-amber-200',
          icon: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>,
          bg: 'bg-amber-50',
          stroke: '#f59e0b'
        };
      case 'likely_misapplied':
        return {
          label: 'LIKELY MISAPPLIED',
          color: 'bg-red-100 text-red-800 border-red-200',
          icon: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>,
          bg: 'bg-red-50',
          stroke: '#ef4444'
        };
      case 'insufficient_evidence':
      default:
        return {
          label: 'INSUFFICIENT EVIDENCE',
          color: 'bg-gray-100 text-gray-800 border-gray-200',
          icon: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>,
          bg: 'bg-gray-50',
          stroke: '#6b7280'
        };
    }
  };

  const config = getVerdictConfig();

  return (
    <div className={`p-8 rounded-3xl border ${config.color} ${config.bg} flex flex-col items-center justify-center animate-scale-in text-center shadow-sm`}>
      <div className={`w-16 h-16 rounded-2xl flex items-center justify-center mb-4 text-white`} style={{ backgroundColor: config.stroke }}>
        {config.icon}
      </div>
      <h2 className="text-3xl font-bold mb-2 tracking-tight">{config.label}</h2>
      
      {consistencyScore !== undefined && (
        <div className="mt-4 flex flex-col items-center gap-1 opacity-80">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-sm">Consistency Score:</span>
            <span className="bg-white/50 px-2 py-0.5 rounded text-sm font-bold border border-black/10">
              {consistencyScore}/3
            </span>
          </div>
          <p className="text-xs">Measures agreement between reasoning passes, not probability of correctness.</p>
        </div>
      )}
    </div>
  );
}
