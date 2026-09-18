import React from 'react';

export default function FinalCTA({ onNavigate }) {
  return (
    <section className="py-24 bg-white relative overflow-hidden">
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute bottom-0 right-0 w-[600px] h-[600px] bg-primary/5 rounded-full blur-[80px] translate-x-1/3 translate-y-1/3" />
      </div>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center">
        <h2 className="text-4xl sm:text-5xl font-black text-navy mb-6 tracking-tight">
          Know where your claim stands.
        </h2>
        <p className="text-xl text-navy/70 mb-10 leading-relaxed font-medium">
          Check your evidence before submission or understand a rejection with policy-grounded analysis.
        </p>
        
        <button
          onClick={() => onNavigate('moduleA')}
          className="bg-primary hover:bg-primary-dark text-white font-bold px-10 py-5 rounded-full text-xl transition-all shadow-[0_8px_30px_rgb(50,129,183,0.3)] hover:shadow-[0_8px_30px_rgb(50,129,183,0.5)] hover:-translate-y-1"
        >
          Check My Claim
        </button>
      </div>
    </section>
  );
}
