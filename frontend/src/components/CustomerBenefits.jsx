import React from 'react';
import { useScrollRevealMultiple } from '../hooks/useScrollReveal';

export default function CustomerBenefits() {
  const setRef = useScrollRevealMultiple(3);

  const benefits = [
    {
      num: "01",
      title: "CHECK BEFORE YOU SUBMIT",
      description: "Know whether your evidence satisfies the policy requirements before you ever file a claim. Identify missing documents or contradictions instantly.",
    },
    {
      num: "02",
      title: "UNDERSTAND A REJECTION",
      description: "Don't just accept a denial. See exactly how the insurer's stated reason compares with the actual wording of your policy.",
    },
    {
      num: "03",
      title: "KNOW WHY",
      description: "Every result is grounded in reality. Trace any conclusion directly back to the specific policy clause and the evidence you provided.",
    }
  ];

  return (
    <section className="py-32 bg-white relative overflow-hidden" id="benefits">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="mb-24 md:w-2/3">
          <h2 className="text-4xl sm:text-5xl lg:text-6xl font-black text-navy mb-8 tracking-tight leading-[1.1]">
            Absolute clarity,<br />
            <span className="text-primary">grounded in your policy.</span>
          </h2>
        </div>

        <div className="grid md:grid-cols-3 gap-12 lg:gap-20">
          {benefits.map((benefit, idx) => (
            <div 
              key={idx}
              ref={setRef(idx)}
              className="scroll-reveal group relative border-t-2 border-navy/10 pt-8 hover:border-primary transition-colors duration-500"
            >
              <div className="text-sm font-black text-primary/40 mb-6 tracking-widest font-mono group-hover:text-primary transition-colors duration-500">
                {benefit.num}
              </div>
              <h3 className="text-2xl font-black text-navy mb-6 tracking-tight leading-snug uppercase">
                {benefit.title}
              </h3>
              <p className="text-navy/70 text-lg leading-relaxed font-medium">
                {benefit.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
