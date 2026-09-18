import React from 'react';
import { useScrollReveal } from '../hooks/useScrollReveal';

export default function TrustSection() {
  const ref = useScrollReveal();

  return (
    <section className="py-32 bg-navy text-white relative overflow-hidden">
      {/* Background radial gradient */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-primary/20 rounded-full blur-[100px] pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div ref={ref} className="scroll-reveal text-center mb-20">
          <h2 className="text-4xl sm:text-5xl font-black mb-6 tracking-tight">
            Built for Evidence,<br />
            <span className="text-highlight">Not Guesswork.</span>
          </h2>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          <div className="bg-white/5 border border-white/10 rounded-[2rem] p-10 hover:bg-white/10 hover:border-white/20 transition-all duration-500 hover:-translate-y-2 group backdrop-blur-sm">
            <div className="w-14 h-14 bg-highlight/20 rounded-2xl flex items-center justify-center mb-8 text-highlight group-hover:scale-110 transition-transform">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
            </div>
            <h3 className="text-2xl font-bold mb-4 tracking-tight">Grounded in Your Policy</h3>
            <p className="text-white/60 leading-relaxed font-medium">
              Every result is directly tied to the specific wording in your policy documents. We don't guess or make assumptions.
            </p>
          </div>

          <div className="bg-white/5 border border-white/10 rounded-[2rem] p-10 hover:bg-white/10 hover:border-white/20 transition-all duration-500 hover:-translate-y-2 group backdrop-blur-sm">
            <div className="w-14 h-14 bg-accent-2/20 rounded-2xl flex items-center justify-center mb-8 text-accent-2 group-hover:scale-110 transition-transform">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
            </div>
            <h3 className="text-2xl font-bold mb-4 tracking-tight">Consistent & Fair</h3>
            <p className="text-white/60 leading-relaxed font-medium">
              Dates, limits, and requirements are checked exactly the same way every time, ensuring you get an accurate and unbiased view.
            </p>
          </div>

          <div className="bg-white/5 border border-white/10 rounded-[2rem] p-10 hover:bg-white/10 hover:border-white/20 transition-all duration-500 hover:-translate-y-2 group backdrop-blur-sm">
            <div className="w-14 h-14 bg-accent-3/20 rounded-2xl flex items-center justify-center mb-8 text-accent-3 group-hover:scale-110 transition-transform">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
            </div>
            <h3 className="text-2xl font-bold mb-4 tracking-tight">Honest Answers</h3>
            <p className="text-white/60 leading-relaxed font-medium">
              If a document is missing or illegible, the system will tell you clearly rather than trying to invent a definitive answer.
            </p>
          </div>
        </div>

        {/* Evidence Trace visualization at bottom of Trust section */}
        <div className="mt-24 pt-16 border-t border-white/10 text-center">
            <h3 className="text-sm font-bold text-white/50 tracking-widest uppercase mb-8">Transparent Evidence Trace</h3>
            <div className="flex flex-col md:flex-row items-center justify-center gap-4 md:gap-8 opacity-80">
               {['VERDICT', 'POLICY CLAUSE', 'EVIDENCE FACT', 'SOURCE DOCUMENT', 'PAGE'].map((node, idx) => (
                  <React.Fragment key={node}>
                    <div className="bg-white/10 px-4 py-2 rounded-lg font-bold text-xs tracking-wider border border-white/20">
                      {node}
                    </div>
                    {idx < 4 && (
                      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-primary hidden md:block"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
                    )}
                    {idx < 4 && (
                      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-primary md:hidden"><line x1="12" y1="5" x2="12" y2="19"/><polyline points="19 12 12 19 5 12"/></svg>
                    )}
                  </React.Fragment>
               ))}
            </div>
        </div>
      </div>
    </section>
  );
}
