import React from 'react';
import { useScrollRevealMultiple } from '../hooks/useScrollReveal';

export default function ImageStorySection() {
  const setRef = useScrollRevealMultiple(2);

  return (
    <section className="py-24 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-32">
        
        {/* Story 1 */}
        <div className="grid md:grid-cols-2 gap-16 items-center">
          <div ref={setRef(0)} className="scroll-reveal order-2 md:order-1 relative">
             <div className="absolute inset-0 bg-surface-1 rounded-3xl translate-x-4 translate-y-4 -z-10" />
             <div className="rounded-3xl overflow-hidden shadow-2xl relative">
                <img 
                  src="https://images.unsplash.com/photo-1554224155-6726b3ff858f?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80" 
                  alt="Person reviewing policy documents"
                  className="w-full h-auto object-cover aspect-[4/3]"
                />
             </div>
          </div>
          
          <div className="order-1 md:order-2">
             <h3 className="text-sm font-bold text-primary tracking-widest uppercase mb-3">Before the claim is submitted</h3>
             <h2 className="text-4xl lg:text-5xl font-black text-navy mb-6 tracking-tight leading-tight">
               Know what's missing before you submit.
             </h2>
             <p className="text-lg text-navy/70 mb-8 leading-relaxed font-medium">
               Upload your documents and policy. We extract the facts and cross-reference them against the required policy conditions so you know exactly where you stand.
             </p>
             
             {/* Card moved from image to here */}
             <div className="bg-white border border-gray-100 rounded-xl p-5 shadow-lg mb-8 inline-block">
                <p className="text-xs font-bold text-navy/50 uppercase tracking-widest mb-1">Detected</p>
                <p className="font-bold text-navy flex items-center gap-2">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
                  Missing Pre-authorization
                </p>
             </div>

             <ul className="space-y-4">
               {['Policy requirements', 'Missing evidence', 'Contradiction detection'].map((item, i) => (
                 <li key={i} className="flex items-center gap-3">
                    <div className="w-6 h-6 rounded-full bg-accent-1/20 flex items-center justify-center text-accent-1">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                    </div>
                    <span className="font-bold text-navy/80">{item}</span>
                 </li>
               ))}
             </ul>
          </div>
        </div>

        {/* Story 2 */}
        <div className="grid md:grid-cols-2 gap-16 items-center">
          <div>
             <h3 className="text-sm font-bold text-accent-3 tracking-widest uppercase mb-3">After the rejection</h3>
             <h2 className="text-4xl lg:text-5xl font-black text-navy mb-6 tracking-tight leading-tight">
               See exactly why a rejection may not hold up.
             </h2>
             <p className="text-lg text-navy/70 mb-8 leading-relaxed font-medium">
               Don't just accept a denial. Upload the rejection letter and your policy to verify if the insurer applied the correct clause and logic.
             </p>

             {/* Card moved from image to here */}
             <div className="bg-white border border-gray-100 rounded-xl p-5 shadow-lg mb-8 inline-block">
                <p className="text-xs font-bold text-navy/50 uppercase tracking-widest mb-1">Verdict</p>
                <p className="font-bold text-navy flex items-center gap-2">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
                  Questionable Rejection
                </p>
             </div>

             <ul className="space-y-4">
               {['Clause matching', 'Consistency analysis', 'Evidence trace', 'Grounded appeal'].map((item, i) => (
                 <li key={i} className="flex items-center gap-3">
                    <div className="w-6 h-6 rounded-full bg-accent-3/20 flex items-center justify-center text-accent-3">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                    </div>
                    <span className="font-bold text-navy/80">{item}</span>
                 </li>
               ))}
             </ul>
          </div>
          
          <div ref={setRef(1)} className="scroll-reveal relative">
             <div className="absolute inset-0 bg-surface-2 rounded-3xl -translate-x-4 translate-y-4 -z-10" />
             <div className="rounded-3xl overflow-hidden shadow-2xl relative">
                <img 
                  src="https://images.unsplash.com/photo-1450101499163-c8848c66ca85?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80" 
                  alt="Person reviewing rejection paperwork"
                  className="w-full h-auto object-cover aspect-[4/3]"
                />
             </div>
          </div>
        </div>
        
      </div>
    </section>
  );
}
