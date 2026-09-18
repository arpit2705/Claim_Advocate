import React from 'react';

export default function Footer({ setCurrentView }) {
  return (
    <footer className="bg-navy text-white py-16 border-t border-white/10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-12 mb-16">
          <div className="col-span-2 md:col-span-1 flex flex-col items-start">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 bg-white/10 rounded-lg flex items-center justify-center backdrop-blur-sm border border-white/20">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#B2FFE6" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
              </div>
              <span className="font-bold text-lg">Claim Advocate</span>
            </div>
            <p className="text-white/60 text-sm font-medium">One engine. Two moments.</p>
          </div>

          <div>
            <h4 className="font-bold text-sm tracking-wider uppercase mb-4 text-white/50">Product</h4>
            <ul className="space-y-3">
              <li>
                <button onClick={() => setCurrentView('moduleA')} className="text-white/80 hover:text-white transition-colors text-sm font-medium">
                  Before You Submit
                </button>
              </li>
              <li>
                <button onClick={() => setCurrentView('moduleB')} className="text-white/80 hover:text-white transition-colors text-sm font-medium">
                  If You're Rejected
                </button>
              </li>
            </ul>
          </div>

          <div>
            <h4 className="font-bold text-sm tracking-wider uppercase mb-4 text-white/50">Company</h4>
            <ul className="space-y-3">
              <li className="text-white/80 hover:text-white transition-colors text-sm font-medium cursor-not-allowed opacity-80">About Claim Advocate</li>
              <li className="text-white/80 hover:text-white transition-colors text-sm font-medium cursor-not-allowed opacity-80">Decision Support</li>
            </ul>
          </div>

          <div>
            <h4 className="font-bold text-sm tracking-wider uppercase mb-4 text-white/50">Legal</h4>
            <ul className="space-y-3">
              <li className="text-white/80 hover:text-white transition-colors text-sm font-medium cursor-not-allowed opacity-80">Privacy</li>
              <li className="text-white/80 hover:text-white transition-colors text-sm font-medium cursor-not-allowed opacity-80">Terms</li>
              <li className="text-white/80 hover:text-white transition-colors text-sm font-medium cursor-not-allowed opacity-80">Disclaimer</li>
            </ul>
          </div>
        </div>

        <div className="pt-8 border-t border-white/10 flex flex-col md:flex-row justify-between items-center gap-4 text-xs text-white/40 font-medium">
          <p>© 2026 Claim Advocate</p>
          <p>Decision-support tool. Not a legally binding adjudicator.</p>
        </div>
      </div>
    </footer>
  );
}
