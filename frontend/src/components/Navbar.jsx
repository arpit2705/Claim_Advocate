import React, { useState, useEffect } from 'react';

export default function Navbar({ currentView, setCurrentView }) {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleNav = (view) => {
    setCurrentView(view);
    setMobileOpen(false);
  };

  return (
    <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
      scrolled || currentView !== 'home'
        ? 'bg-white/90 backdrop-blur-xl shadow-[0_4px_30px_rgba(0,0,0,0.03)] py-3 border-b border-gray-100'
        : 'bg-transparent py-5'
    }`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <button onClick={() => handleNav('home')} className="flex items-center gap-3 group">
            <div className={`w-10 h-10 rounded-xl flex items-center justify-center transition-all duration-300 ${
              scrolled || currentView !== 'home' ? 'bg-primary shadow-md shadow-primary/20' : 'bg-primary/90 shadow-lg shadow-primary/20'
            }`}>
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                <path d="M9 12l2 2 4-4"/>
              </svg>
            </div>
            <span className="text-xl font-black tracking-tight text-navy">
              Claim Advocate
            </span>
          </button>

          {/* Desktop Nav */}
          <div className="hidden md:flex items-center gap-2">
            {[
              { label: 'Home', id: 'home' },
              { label: 'Before You Submit', id: 'moduleA' },
              { label: "If You're Rejected", id: 'moduleB' }
            ].map(({ label, id }) => (
              <button
                key={id}
                onClick={() => handleNav(id)}
                className={`px-4 py-2 rounded-full text-sm font-semibold transition-all hover:bg-primary/5 ${currentView === id ? 'text-primary bg-primary/5' : 'text-navy/70 hover:text-primary'}`}
              >
                {label}
              </button>
            ))}
          </div>

          {/* Right side */}
          <div className="hidden md:flex items-center gap-4">
            <span className="text-xs font-bold px-3 py-1.5 rounded-full border border-accent-3/30 text-accent-3 bg-accent-3/10 tracking-wide uppercase">
              Policy-Grounded AI
            </span>
            <button
              onClick={() => handleNav('moduleA')}
              className="bg-navy hover:bg-black text-white text-sm font-bold px-6 py-2.5 rounded-full transition-all shadow-md hover:shadow-xl hover:-translate-y-0.5"
            >
              Check My Claim
            </button>
          </div>

          {/* Mobile hamburger */}
          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className="md:hidden p-2 text-navy"
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
              {mobileOpen ? (
                <>
                  <line x1="18" y1="6" x2="6" y2="18"/>
                  <line x1="6" y1="6" x2="18" y2="18"/>
                </>
              ) : (
                <>
                  <line x1="3" y1="6" x2="21" y2="6"/>
                  <line x1="3" y1="12" x2="21" y2="12"/>
                  <line x1="3" y1="18" x2="21" y2="18"/>
                </>
              )}
            </svg>
          </button>
        </div>

        {/* Mobile menu */}
        {mobileOpen && (
          <div className="md:hidden mt-4 pb-4 border-t border-gray-100 animate-fade-in-down bg-white rounded-2xl p-4 shadow-xl absolute left-4 right-4 border z-50">
            <div className="flex flex-col gap-2">
              {[
                { label: 'Home', id: 'home' },
                { label: 'Before You Submit', id: 'moduleA' },
                { label: "If You're Rejected", id: 'moduleB' }
              ].map(({ label, id }) => (
                <button
                  key={id}
                  onClick={() => handleNav(id)}
                  className={`text-left px-4 py-3 rounded-xl text-sm font-bold hover:bg-gray-50 ${currentView === id ? 'text-primary' : 'text-navy'}`}
                >
                  {label}
                </button>
              ))}
              <button
                onClick={() => handleNav('moduleA')}
                className="mt-2 bg-primary text-white text-sm font-bold px-5 py-3 rounded-xl"
              >
                Check My Claim
              </button>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}
