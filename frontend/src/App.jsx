import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import CustomerBenefits from './components/CustomerBenefits';
import ImageStorySection from './components/ImageStorySection';
import FinalCTA from './components/FinalCTA';
import Footer from './components/Footer';
import ModuleA from './components/ModuleA';
import ModuleB from './components/ModuleB';

export default function App() {
  // Simple state-based routing: 'home', 'moduleA', 'moduleB'
  const [currentView, setCurrentView] = useState('home');

  // Scroll to top on view change
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [currentView]);

  return (
    <div className="min-h-screen bg-bg font-sans selection:bg-primary/20 selection:text-primary-dark">
      <Navbar currentView={currentView} setCurrentView={setCurrentView} />

      <main className="w-full">
        {currentView === 'home' && (
          <div className="animate-fade-in">
            <Hero onNavigate={setCurrentView} />
            <ImageStorySection />
            <CustomerBenefits />
            <FinalCTA onNavigate={setCurrentView} />
          </div>
        )}

        {currentView === 'moduleA' && (
           <div className="pt-32 pb-24 animate-fade-in min-h-screen bg-bg">
              <ModuleA onNavigate={setCurrentView} />
           </div>
        )}

        {currentView === 'moduleB' && (
           <div className="pt-32 pb-24 animate-fade-in min-h-screen bg-bg">
              <ModuleB onNavigate={setCurrentView} />
           </div>
        )}
      </main>

      <Footer setCurrentView={setCurrentView} />
    </div>
  );
}
