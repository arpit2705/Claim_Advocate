import React from 'react';
import { useScrollRevealMultiple } from '../hooks/useScrollReveal';

export default function ImageStorySection() {
  const setRef = useScrollRevealMultiple(2);

  return (
    <section className="py-24 bg-bg overflow-hidden relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Story 1 */}
        <div className="mb-40">
           <h2 className="text-4xl sm:text-5xl lg:text-6xl font-black text-navy mb-16 tracking-tight leading-[1.1] max-w-2xl">
             Insurance shouldn't feel like a guessing game.
           </h2>

           <div className="grid md:grid-cols-2 gap-16 items-center">
             <div ref={setRef(0)} className="scroll-reveal relative">
                <div className="rounded-3xl overflow-hidden shadow-2xl relative">
                   <img 
                     src="https://images.unsplash.com/photo-1554224155-6726b3ff858f?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80" 
                     alt="Person reviewing policy documents"
                     className="w-full h-auto object-cover aspect-[4/3]"
                   />
                </div>
                
                {/* Floating Result Panel overlapping slightly on the right */}
                <div className="absolute -bottom-6 -right-6 bg-white/90 backdrop-blur border border-primary/20 rounded-2xl p-5 shadow-[0_20px_40px_rgba(0,0,0,0.1)] w-48 animate-float hidden sm:block z-10">
                   <p className="text-[10px] font-bold text-navy/40 uppercase tracking-widest mb-1">Readiness</p>
                   <p className="text-3xl font-black text-primary mb-1 tracking-tight">92 / 100</p>
                </div>
             </div>
             
             <div>
                <h3 className="text-3xl lg:text-4xl font-black text-navy mb-6 tracking-tight leading-tight">
                  Know what's missing before you submit.
                </h3>
                <p className="text-lg text-navy/70 mb-8 leading-relaxed font-medium">
                  Claim Advocate checks the evidence against policy requirements so you know exactly where you stand before filing a claim.
                </p>
                
                {/* Integrated Detected Card */}
                <div className="bg-white border border-red-100 rounded-2xl p-5 shadow-md w-full max-w-xs">
                   <p className="text-[10px] font-bold text-red-500/70 uppercase tracking-widest mb-2">Document Check</p>
                   <p className="font-bold text-red-900 flex items-center gap-3">
                     <span className="w-8 h-8 rounded-full bg-red-50 flex items-center justify-center shrink-0">
                       <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
                     </span>
                     Missing hospital invoice
                   </p>
                </div>
             </div>
           </div>
        </div>

        {/* Story 2 */}
        <div>
           <div className="grid md:grid-cols-2 gap-16 items-center">
             <div className="order-2 md:order-1">
                <h2 className="text-3xl lg:text-4xl font-black text-navy mb-6 tracking-tight leading-tight">
                  Rejected doesn't always mean finished.
                </h2>
                <p className="text-lg text-navy/70 leading-relaxed font-medium">
                  See whether the reason given by your insurer actually matches your policy. Don't just accept a denial without verification.
                </p>
             </div>
             
             <div ref={setRef(1)} className="scroll-reveal relative order-1 md:order-2 mt-8 md:mt-0">
                <div className="rounded-3xl overflow-hidden shadow-2xl relative">
                   <img 
                     src="https://images.unsplash.com/photo-1450101499163-c8848c66ca85?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80" 
                     alt="Person reviewing rejection paperwork"
                     className="w-full h-auto object-cover aspect-[4/3]"
                   />
                </div>

                {/* Floating Rejection Analysis Panel overlapping slightly */}
                <div className="absolute -top-6 -left-6 bg-white/90 backdrop-blur border border-amber-500/20 rounded-2xl p-5 shadow-[0_20px_40px_rgba(0,0,0,0.1)] w-56 animate-float z-10 hidden sm:block" style={{animationDelay: '1s'}}>
                   <p className="text-[10px] font-bold text-navy/40 uppercase tracking-widest mb-1">Rejection Analysis</p>
                   <p className="text-2xl font-black text-amber-500 mb-2 tracking-tight">QUESTIONABLE</p>
                   <div className="flex justify-between items-center border-t border-gray-100 pt-2 mt-2">
                     <span className="text-[10px] font-bold text-navy/60 uppercase">Consistency</span>
                     <span className="text-[10px] font-bold text-primary uppercase">3 / 3 checks agree</span>
                   </div>
                </div>
             </div>
           </div>
        </div>
        
      </div>
    </section>
  );
}
