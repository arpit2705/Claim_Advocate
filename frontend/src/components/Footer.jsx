import React from 'react';

export default function Footer() {
  return (
    <footer className="bg-navy text-white py-16 border-t border-white/10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="flex flex-col items-center md:items-start">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-8 h-8 bg-white/10 rounded-lg flex items-center justify-center backdrop-blur-sm border border-white/20">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#B2FFE6" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
              </div>
              <span className="font-bold text-lg">Claim Advocate</span>
            </div>
            <p className="text-white/50 text-sm">One engine. Two moments. Better-informed claims.</p>
          </div>
          
          <div className="flex flex-wrap justify-center gap-6 text-sm text-white/60">
            <a href="#module-a" className="hover:text-white transition-colors">Before You Submit</a>
            <a href="#module-b" className="hover:text-white transition-colors">If You're Rejected</a>
            <a href="#engine" className="hover:text-white transition-colors">How It Works</a>
          </div>
        </div>
        
        <div className="mt-12 pt-8 border-t border-white/10 flex flex-col md:flex-row justify-between items-center gap-4 text-xs text-white/40">
          <p>Built for Paytm Build for India Hackathon.</p>
          <p className="flex items-center gap-1.5 bg-white/5 px-3 py-1.5 rounded-full border border-white/10">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
            Decision-support tool. Not a legally binding adjudicator.
          </p>
        </div>
      </div>
    </footer>
  );
}
