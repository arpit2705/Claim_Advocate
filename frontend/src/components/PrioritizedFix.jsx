import React from 'react';

export default function PrioritizedFix({ fix, index }) {
  return (
    <div
      className="flex gap-4 p-5 bg-white border border-gray-100 rounded-2xl card-hover animate-fade-in-up"
      style={{ animationDelay: `${index * 0.1}s` }}
    >
      <div className="w-10 h-10 bg-primary/10 rounded-xl flex items-center justify-center flex-shrink-0">
        <span className="text-primary font-bold text-sm">{index + 1}</span>
      </div>
      <p className="text-gray-700 text-sm leading-relaxed pt-2">{fix}</p>
    </div>
  );
}
