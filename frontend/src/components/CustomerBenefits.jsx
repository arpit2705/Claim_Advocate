import React from 'react';
import { useScrollRevealMultiple } from '../hooks/useScrollReveal';

export default function CustomerBenefits() {
  const setRef = useScrollRevealMultiple(4);

  const cards = [
    {
      title: "Check Before You Submit",
      description: "Know whether your documents meet your policy requirements before filing.",
      color: "bg-surface-1",
      border: "border-primary/20",
      iconColor: "text-primary",
      icon: (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><path d="M9 15l2 2 4-4"/></svg>
      )
    },
    {
      title: "Spot What's Missing",
      description: "Find missing evidence and important inconsistencies before they become a problem.",
      color: "bg-[#FFF5F0]", // very soft orange/peach tint from tailwind defaults or just white
      border: "border-amber-200",
      iconColor: "text-amber-500",
      icon: (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
      )
    },
    {
      title: "Understand a Rejection",
      description: "See whether the reason for rejection actually matches your policy.",
      color: "bg-surface-2",
      border: "border-accent-3/30",
      iconColor: "text-accent-3",
      icon: (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
      )
    },
    {
      title: "Know Why",
      description: "Trace the result back to the policy clause and evidence used.",
      color: "bg-primary/5",
      border: "border-accent-1/30",
      iconColor: "text-accent-1",
      icon: (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
      )
    }
  ];

  return (
    <section className="py-24 bg-white relative overflow-hidden" id="benefits">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="text-center mb-16">
          <h2 className="text-4xl sm:text-5xl font-black text-navy mb-6 tracking-tight">
            Everything You Need to <br className="hidden sm:block" />
            <span className="text-primary">Understand Your Claim.</span>
          </h2>
          <p className="text-navy/60 text-lg md:text-xl max-w-2xl mx-auto font-medium leading-relaxed">
            Get absolute clarity on where you stand, whether you are preparing to submit or questioning a decision.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {cards.map((card, idx) => (
            <div 
              key={idx}
              ref={setRef(idx)}
              className="scroll-reveal group relative bg-white border border-gray-100 rounded-[2rem] p-8 shadow-lg shadow-navy/5 hover:shadow-xl hover:-translate-y-2 transition-all duration-500 ease-[cubic-bezier(0.16,1,0.3,1)] overflow-hidden"
            >
              {/* Subtle animated background shift on hover */}
              <div className={`absolute inset-0 ${card.color} opacity-0 group-hover:opacity-40 transition-opacity duration-500`} />
              
              <div className="relative z-10">
                <div className={`w-14 h-14 rounded-2xl flex items-center justify-center mb-8 ${card.color} ${card.iconColor} shadow-sm group-hover:scale-110 group-hover:rotate-3 transition-transform duration-500`}>
                  {card.icon}
                </div>
                <h3 className="text-2xl font-bold text-navy mb-4 tracking-tight leading-snug">{card.title}</h3>
                <p className="text-navy/70 font-medium leading-relaxed">
                  {card.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
