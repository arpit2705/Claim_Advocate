import React, { useState } from 'react';
import InsuranceGlobe from './InsuranceGlobe';

export default function Hero({ onCheckClaim, onSeeHow }) {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <section 
      id="hero" 
      className="relative min-h-screen pt-24 pb-16 flex items-center overflow-hidden bg-bg"
    >
      {/* Abstract Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] right-[-5%] w-[800px] h-[800px] bg-surface-1/40 rounded-full blur-3xl opacity-60" />
        <div className="absolute bottom-[-10%] left-[-10%] w-[600px] h-[600px] bg-surface-2/30 rounded-full blur-3xl opacity-50" />
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full z-10">
        <div className="grid lg:grid-cols-12 gap-12 items-center">
          
          {/* Left: Typography & CTAs */}
          <div className="lg:col-span-5 animate-fade-in-up z-20">
            <h1 className="text-5xl sm:text-6xl lg:text-7xl font-extrabold text-navy leading-[1.1] mb-6 tracking-tight">
              Know Your Policy.
              <br />
              <span className="text-primary">Before You Need It.</span>
            </h1>

            <p className="text-lg text-navy/70 max-w-lg mb-10 leading-relaxed font-medium">
              Check your evidence before submitting a claim, or understand whether a rejection actually matches your policy.
            </p>

            <div className="flex flex-wrap gap-4 mb-10">
              <button
                onClick={onCheckClaim}
                className="bg-primary hover:bg-primary-dark text-white font-bold px-8 py-4 rounded-full text-lg transition-all shadow-[0_8px_30px_rgb(50,129,183,0.3)] hover:shadow-[0_8px_30px_rgb(50,129,183,0.5)] hover:-translate-y-1"
              >
                Check My Claim
              </button>
              <button
                onClick={onSeeHow}
                className="bg-white border-2 border-primary/10 text-primary hover:border-primary/30 font-bold px-8 py-4 rounded-full text-lg transition-all hover:bg-surface-1/30"
              >
                See How It Works
              </button>
            </div>
            
            <div className="flex flex-col gap-2">
              <p className="text-sm font-bold text-navy/80 uppercase tracking-widest mb-1">Clear Outcomes</p>
              <div className="flex items-center gap-6 text-sm text-navy/60 font-medium">
                <span className="flex items-center gap-1.5"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-accent-3"><polyline points="20 6 9 17 4 12"/></svg> Know what's missing</span>
                <span className="flex items-center gap-1.5"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-accent-3"><polyline points="20 6 9 17 4 12"/></svg> Understand decisions</span>
              </div>
            </div>
          </div>

          {/* Right: Interactive Globe */}
          <div 
            className="lg:col-span-7 relative h-[600px] w-full flex items-center justify-center"
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
          >
            {/* The Globe */}
            <div className="absolute inset-0 z-0 scale-110 lg:scale-125 origin-center transition-transform duration-1000 ease-out"
                 style={{ transform: `scale(${isHovered ? 1.3 : 1.25})` }}>
               <InsuranceGlobe />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
