import React from 'react';

export default function LoadingState({ message }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 animate-fade-in">
      <div className="relative mb-6">
        <div className="w-16 h-16 border-4 border-gray-200 rounded-full" />
        <div className="absolute inset-0 w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin-slow" />
      </div>
      <p className="text-lg font-semibold text-navy mb-2">
        {message || 'Analyzing your documents...'}
      </p>
      <p className="text-sm text-gray-400 max-w-sm text-center">
        Our engine is extracting policy clauses, checking requirements, and validating evidence.
      </p>
      <div className="mt-6 flex gap-1.5">
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            className="w-2.5 h-2.5 bg-primary/40 rounded-full"
            style={{
              animation: 'pulse 1.4s ease-in-out infinite',
              animationDelay: `${i * 0.2}s`,
            }}
          />
        ))}
      </div>
    </div>
  );
}
