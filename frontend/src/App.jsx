import React, { useState } from 'react';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import EngineSection from './components/EngineSection';
import ModuleTabs from './components/ModuleTabs';
import ModuleA from './components/ModuleA';
import ModuleB from './components/ModuleB';
import CustomerBenefits from './components/CustomerBenefits';
import ImageStorySection from './components/ImageStorySection';
import TrustSection from './components/TrustSection';
import Footer from './components/Footer';

export default function App() {
  const [activeTab, setActiveTab] = useState('readiness');

  const scrollToModules = () => {
    const el = document.getElementById('modules');
    if (el) {
      // Add slight offset for sticky navbar
      const y = el.getBoundingClientRect().top + window.scrollY - 100;
      window.scrollTo({ top: y, behavior: 'smooth' });
    }
  };

  const scrollToEngine = () => {
    const el = document.getElementById('engine');
    if (el) {
      const y = el.getBoundingClientRect().top + window.scrollY - 100;
      window.scrollTo({ top: y, behavior: 'smooth' });
    }
  };

  return (
    <div className="min-h-screen flex flex-col font-sans selection:bg-primary/20 selection:text-navy">
      <Navbar />
      
      <main className="flex-1">
        <Hero 
          onCheckClaim={scrollToModules}
          onSeeHow={scrollToEngine}
        />
        
        <EngineSection />
        
        <ImageStorySection />
        
        <CustomerBenefits />
        
        <section id="modules" className="py-24 bg-gray-50/50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="mb-12">
              <ModuleTabs 
                activeTab={activeTab} 
                onTabChange={setActiveTab} 
              />
            </div>
            
            <div className="bg-white rounded-[2.5rem] shadow-xl shadow-navy/5 overflow-hidden border border-gray-100">
              <div className="transition-all duration-500 ease-in-out">
                {activeTab === 'readiness' ? <ModuleA /> : <ModuleB />}
              </div>
            </div>
          </div>
        </section>

        <section id="how-it-works" className="py-24 bg-white">
           <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
             <div className="text-center mb-16 scroll-reveal">
                <h2 className="text-3xl sm:text-4xl font-bold text-navy mb-4">How Claim Advocate Works</h2>
                <p className="text-gray-500 text-lg max-w-2xl mx-auto">
                  A transparent pipeline combining LLM reasoning with deterministic code validation.
                </p>
             </div>
             
             <div className="relative">
                <div className="absolute left-[28px] md:left-1/2 top-4 bottom-4 w-1 bg-gradient-to-b from-primary/20 via-secondary/20 to-primary/20 md:-translate-x-1/2 rounded-full" />
                
                <div className="space-y-12 relative">
                  {[
                    { title: "Document Extraction", desc: "PDFs are converted to structured text and facts." },
                    { title: "Policy Knowledge Retrieval", desc: "Relevant clauses are pulled using hybrid search." },
                    { title: "LLM Reasoning Passes", desc: "Multiple independent model calls propose outcomes." },
                    { title: "Deterministic Validation", desc: "Code strictly validates dates, numbers, and limits." },
                    { title: "Decision Grounding", desc: "Final result is explicitly tied back to source evidence." },
                  ].map((step, i) => (
                    <div key={i} className={`flex flex-col md:flex-row items-start md:items-center gap-6 ${i % 2 === 0 ? 'md:flex-row-reverse text-left md:text-right' : 'text-left'} animate-fade-in-up`} style={{animationDelay: `${i * 0.15}s`}}>
                      <div className="w-full md:w-1/2 flex flex-col items-start md:items-center">
                        <div className={`pl-16 md:pl-0 ${i % 2 === 0 ? 'md:pr-12' : 'md:pl-12'}`}>
                          <h4 className="text-xl font-bold text-navy mb-2">{step.title}</h4>
                          <p className="text-gray-600">{step.desc}</p>
                        </div>
                      </div>
                      <div className="absolute left-0 md:left-1/2 w-14 h-14 bg-white border-4 border-gray-100 rounded-full flex items-center justify-center text-primary font-bold md:-translate-x-1/2 shadow-sm z-10">
                        {i + 1}
                      </div>
                    </div>
                  ))}
                </div>
                
                <div className="mt-16 text-center">
                  <p className="inline-flex items-center gap-2 bg-navy text-white px-6 py-3 rounded-full font-semibold shadow-lg">
                    LLM proposes reasoning → deterministic validation → final result
                  </p>
                </div>
             </div>
           </div>
        </section>

        <TrustSection />
      </main>

      <Footer />
    </div>
  );
}
