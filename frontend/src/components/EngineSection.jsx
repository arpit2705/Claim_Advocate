import React from 'react';
import { useScrollReveal } from '../hooks/useScrollReveal';

export default function EngineSection() {
  const ref = useScrollReveal();

  return (
    <section className="py-32 bg-white relative overflow-hidden" id="engine">
      {/* Background accents */}
      <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-surface-1/50 rounded-full blur-3xl opacity-50 translate-x-1/2 -translate-y-1/2 pointer-events-none" />
      <div className="absolute bottom-0 left-0 w-[400px] h-[400px] bg-highlight/30 rounded-full blur-3xl opacity-50 -translate-x-1/2 translate-y-1/2 pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div ref={ref} className="scroll-reveal text-center mb-20">
          <h2 className="text-4xl sm:text-5xl lg:text-6xl font-black text-navy mb-6 tracking-tight">
            ONE ENGINE.<br/>
            <span className="text-primary">TWO MOMENTS.</span>
          </h2>
          <p className="text-navy/60 text-lg md:text-xl max-w-2xl mx-auto font-medium leading-relaxed">
            The same policy-grounded reasoning engine helps you prepare before a claim and understand what happened after a rejection.
          </p>
        </div>

        <div className="relative">
          {/* Two module cards */}
          <div className="grid md:grid-cols-2 gap-10 mb-16">
            {/* Module A Card */}
            <div className="group bg-white border border-gray-200 hover:border-primary/30 rounded-[2rem] p-10 shadow-lg shadow-navy/5 hover:shadow-xl hover:shadow-primary/10 transition-all duration-500 hover:-translate-y-1">
              <div className="w-16 h-16 bg-surface-1 rounded-2xl flex items-center justify-center mb-8 text-primary shadow-sm">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                  <polyline points="14 2 14 8 20 8"/>
                  <path d="M9 15l2 2 4-4"/>
                </svg>
              </div>
              <h3 className="text-3xl font-bold text-navy mb-3 tracking-tight">Before You Submit</h3>
              <p className="text-navy/60 text-lg mb-8 font-medium">Check your evidence before filing.</p>
              
              <div className="space-y-4 mb-10">
                {['Readiness Score', 'Requirement Checks', 'Missing Evidence', 'Prioritized Fixes'].map((item) => (
                  <div key={item} className="flex items-center gap-4">
                    <div className="w-6 h-6 bg-accent-2/20 rounded-full flex items-center justify-center flex-shrink-0 text-accent-1">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                        <polyline points="20 6 9 17 4 12"/>
                      </svg>
                    </div>
                    <span className="text-navy/80 font-bold text-sm tracking-wide">{item}</span>
                  </div>
                ))}
              </div>
              
              <button 
                onClick={() => document.getElementById('modules').scrollIntoView({behavior: 'smooth'})}
                className="text-primary font-bold inline-flex items-center gap-2 group-hover:gap-3 transition-all"
              >
                Explore Readiness <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
              </button>
            </div>

            {/* Module B Card */}
            <div className="group bg-white border border-gray-200 hover:border-accent-3/30 rounded-[2rem] p-10 shadow-lg shadow-navy/5 hover:shadow-xl hover:shadow-accent-3/10 transition-all duration-500 hover:-translate-y-1">
              <div className="w-16 h-16 bg-highlight/30 rounded-2xl flex items-center justify-center mb-8 text-accent-3 shadow-sm">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M12 2L3 7v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7l-9-5z"/>
                  <circle cx="12" cy="12" r="3"/>
                </svg>
              </div>
              <h3 className="text-3xl font-bold text-navy mb-3 tracking-tight">If You're Rejected</h3>
              <p className="text-navy/60 text-lg mb-8 font-medium">Understand whether the rejection matches your policy.</p>
              
              <div className="space-y-4 mb-10">
                {['Verdict', 'Consistency Score', 'Policy Clause Match', 'Appeal Letter'].map((item) => (
                  <div key={item} className="flex items-center gap-4">
                    <div className="w-6 h-6 bg-accent-3/20 rounded-full flex items-center justify-center flex-shrink-0 text-accent-3">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                        <polyline points="20 6 9 17 4 12"/>
                      </svg>
                    </div>
                    <span className="text-navy/80 font-bold text-sm tracking-wide">{item}</span>
                  </div>
                ))}
              </div>
              
              <button 
                 onClick={() => {
                   // This assumes we have a way to switch tabs externally, or we just scroll to the section
                   document.getElementById('modules').scrollIntoView({behavior: 'smooth'})
                 }}
                className="text-accent-3 font-bold inline-flex items-center gap-2 group-hover:gap-3 transition-all"
              >
                Analyze Rejection <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
              </button>
            </div>
          </div>

          {/* Engine connector */}
          <div className="flex flex-col items-center relative">
            <div className="w-0.5 h-16 bg-gradient-to-b from-gray-200 via-primary/50 to-primary relative overflow-hidden">
               <div className="absolute top-0 left-0 w-full h-1/2 bg-white opacity-80 animate-trace-reveal" style={{animationDuration: '2s', animationIterationCount: 'infinite'}} />
            </div>
            
            <div className="bg-navy text-white px-8 py-5 rounded-full shadow-2xl flex items-center gap-4 z-10 border border-white/10">
              <div className="w-10 h-10 bg-primary/20 rounded-full flex items-center justify-center">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#67CFC3" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
                </svg>
              </div>
              <div>
                <p className="font-bold tracking-widest uppercase text-sm">Claim Advocate Engine</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
