import React, { useState } from 'react';
import InsuranceGlobe from './InsuranceGlobe';

export default function Hero({ onNavigate }) {
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
                onClick={() => onNavigate('moduleA')}
                className="bg-primary hover:bg-primary-dark text-white font-bold px-10 py-5 rounded-full text-lg transition-all shadow-[0_8px_30px_rgb(50,129,183,0.3)] hover:shadow-[0_8px_30px_rgb(50,129,183,0.5)] hover:-translate-y-1"
              >
                Check My Claim
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

            {/* Scattered UI Panels */}
            {/* Top Right Panel */}
            <div className={`absolute -top-4 right-8 bg-white/90 backdrop-blur border border-primary/20 rounded-2xl p-4 shadow-[0_10px_40px_rgba(50,129,183,0.15)] z-20 transition-all duration-[2000ms] ease-in-out ${isHovered ? 'translate-y-2 -translate-x-2' : ''}`}>
              <p className="text-[10px] font-bold text-navy/40 uppercase tracking-widest mb-1">Readiness</p>
              <p className="text-xl font-black text-primary mb-0.5 tracking-tight">92 / 100</p>
            </div>

            {/* Middle Left Panel */}
            <div className={`absolute top-1/3 -left-4 bg-white/90 backdrop-blur border border-accent-3/20 rounded-2xl p-4 shadow-[0_10px_40px_rgba(103,207,195,0.15)] z-20 transition-all duration-[2500ms] ease-in-out ${isHovered ? '-translate-y-4 translate-x-2' : ''}`}>
              <p className="text-[10px] font-bold text-navy/40 uppercase tracking-widest mb-1">Policy Check</p>
              <p className="text-sm font-bold text-navy tracking-tight">Requirement Satisfied</p>
            </div>

            {/* Bottom Right Panel */}
            <div className={`absolute bottom-16 right-0 bg-white/90 backdrop-blur border border-amber-500/20 rounded-2xl p-4 shadow-[0_10px_40px_rgba(245,158,11,0.15)] z-20 transition-all duration-[3000ms] ease-in-out ${isHovered ? '-translate-y-2 -translate-x-4' : ''}`}>
              <p className="text-[10px] font-bold text-navy/40 uppercase tracking-widest mb-1">Rejection Analysis</p>
              <p className="text-sm font-bold text-navy tracking-tight text-amber-500">Questionable</p>
            </div>
            
          </div>
        </div>
      </div>
    </section>
  );
}
