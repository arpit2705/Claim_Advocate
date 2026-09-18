import React, { useState } from 'react';
import FileUpload from './FileUpload';
import LoadingState from './LoadingState';
import ErrorAlert from './ErrorAlert';
import ReadinessScore from './ReadinessScore';
import RequirementCheck from './RequirementCheck';
import PrioritizedFix from './PrioritizedFix';
import { checkReadiness } from '../services/api';
import { mockReadinessResult, mockReadinessResultValid } from '../data/mockData';

export default function ModuleA() {
  const [policyFiles, setPolicyFiles] = useState([]);
  const [claimFiles, setClaimFiles] = useState([]);
  const [status, setStatus] = useState('idle'); // idle | loading | success | error
  const [errorMessage, setErrorMessage] = useState(null);
  const [result, setResult] = useState(null);

  const canSubmit = policyFiles.length > 0 && claimFiles.length > 0;

  const handleSubmit = async () => {
    if (!canSubmit) return;
    setStatus('loading');
    setErrorMessage(null);
    
    try {
      const data = await checkReadiness(policyFiles[0], claimFiles);
      setResult(data);
      setStatus('success');
    } catch (err) {
      console.error(err);
      setErrorMessage(err.message);
      setStatus('error');
    }
  };

  const handleReset = () => {
    setPolicyFiles([]);
    setClaimFiles([]);
    setStatus('idle');
    setErrorMessage(null);
    setResult(null);
  };

  return (
    <div className="max-w-6xl mx-auto p-4 sm:p-6 lg:p-8 animate-fade-in" id="module-a">
      {status === 'idle' && (
        <div className="text-center mb-16 mt-8">
          <p className="text-primary font-black uppercase tracking-widest text-sm mb-4">Before You Submit</p>
          <h2 className="text-4xl md:text-5xl font-black text-navy mb-6 tracking-tight">Know what's required before you file.</h2>
          <p className="text-xl text-navy/70 font-medium max-w-2xl mx-auto">Upload your policy and claim evidence to see whether you're ready to submit.</p>
        </div>
      )}

      {status === 'idle' && (
        <div className="space-y-8 max-w-3xl mx-auto">
          <div className="bg-white rounded-3xl p-8 md:p-10 shadow-lg border border-gray-100 transition-all hover:shadow-xl">
            <h3 className="text-sm font-bold text-navy/50 mb-2 tracking-widest uppercase">Policy</h3>
            <p className="text-xl font-bold text-navy mb-6">Upload your insurance policy document</p>
            
            <div className="mt-2">
              <FileUpload 
                label="" 
                sublabel=""
                accept=".pdf"
                multiple={false}
                files={policyFiles}
                onFilesChange={setPolicyFiles}
                customStyle="border-2 border-dashed border-gray-200 rounded-2xl p-10 hover:border-primary/50 hover:bg-gray-50 transition-colors"
              />
            </div>
          </div>

          <div className="bg-white rounded-3xl p-8 md:p-10 shadow-lg border border-gray-100 transition-all hover:shadow-xl">
            <h3 className="text-sm font-bold text-navy/50 mb-2 tracking-widest uppercase">Claim Evidence</h3>
            <p className="text-xl font-bold text-navy mb-6">Upload bills, discharge summaries, FIRs and other supporting documents</p>
            
            <div className="mt-2">
              <FileUpload 
                label="" 
                sublabel=""
                accept=".pdf,.png,.jpg,.jpeg"
                multiple={true}
                files={claimFiles}
                onFilesChange={setClaimFiles}
                customStyle="border-2 border-dashed border-gray-200 rounded-2xl p-10 hover:border-primary/50 hover:bg-gray-50 transition-colors"
                icon={<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>}
              />
            </div>
          </div>

          <div className="flex justify-center pt-8">
            <button
              onClick={handleSubmit}
              disabled={!canSubmit}
              className={`px-12 py-5 rounded-full font-bold text-xl transition-all shadow-[0_8px_30px_rgb(50,129,183,0.3)] hover:-translate-y-1 ${
                canSubmit 
                  ? 'bg-primary hover:bg-primary-dark text-white hover:shadow-[0_8px_30px_rgb(50,129,183,0.5)]' 
                  : 'bg-gray-200 text-gray-400 cursor-not-allowed shadow-none hover:translate-y-0'
              }`}
            >
              Check Readiness
            </button>
          </div>
        </div>
      )}

      {status === 'loading' && <LoadingState />}

      {status === 'error' && (
        <ErrorAlert message={errorMessage} onRetry={() => { setStatus('idle'); setErrorMessage(null); }} />
      )}

      {status === 'success' && result && (
        <div className="space-y-12 animate-fade-in-up">
          <div className="flex flex-col md:flex-row items-center justify-between gap-8 bg-white p-8 rounded-3xl shadow-sm border border-gray-100">
            <div className="flex-1 text-center md:text-left">
              <h3 className="text-2xl font-bold text-navy mb-2">Readiness Analysis Complete</h3>
              <p className="text-gray-600 mb-6 max-w-md">
                We've compared your evidence against your policy requirements. Here's how ready your claim is for submission.
              </p>
              <button 
                onClick={handleReset}
                className="text-sm font-semibold text-primary hover:text-primary-dark"
              >
                ← Check another claim
              </button>
            </div>
            <div className="shrink-0 flex justify-center w-full md:w-auto">
              <ReadinessScore score={result.readiness_score} grounded={result.grounded} />
            </div>
          </div>

          {result.prioritized_fixes && result.prioritized_fixes.length > 0 && (
            <div>
              <h3 className="text-xl font-bold text-navy mb-4 flex items-center gap-2">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#67CFC3" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
                Prioritized Fixes
              </h3>
              <div className="space-y-4">
                {result.prioritized_fixes.map((fix, i) => (
                  <PrioritizedFix key={i} fix={fix} index={i} />
                ))}
              </div>
            </div>
          )}

          <div>
            <h3 className="text-xl font-bold text-navy mb-4 flex items-center gap-2">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#3281B7" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="9 11 12 14 22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>
              Requirement Checks
            </h3>
            <div className="grid md:grid-cols-2 gap-4">
              {result.rule_results.map((rule, i) => (
                <RequirementCheck key={i} rule={rule} index={i} />
              ))}
            </div>
          </div>
          
          <div>
            <h3 className="text-xl font-bold text-navy mb-4 flex items-center gap-2 text-amber-700">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
              Contradictions Found
            </h3>
            {result.contradictions && result.contradictions.length > 0 ? (
              <div className="space-y-4">
                {result.contradictions.map((contra, i) => (
                  <div key={i} className="bg-amber-50 border border-amber-200 rounded-2xl p-5">
                    <p className="font-semibold text-amber-900 mb-2">{contra.note}</p>
                    <div className="grid md:grid-cols-2 gap-4 text-sm mt-3">
                      <div className="bg-white/60 p-3 rounded-lg border border-amber-100">
                        <span className="text-xs text-amber-600/70 font-bold uppercase block mb-1">{contra.source_a}</span>
                        <span className="font-medium">{contra.field}: {contra.value_a}</span>
                      </div>
                      <div className="bg-white/60 p-3 rounded-lg border border-amber-100">
                        <span className="text-xs text-amber-600/70 font-bold uppercase block mb-1">{contra.source_b}</span>
                        <span className="font-medium">{contra.field}: {contra.value_b}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="bg-green-50 border border-green-200 rounded-2xl p-5 text-green-800 flex items-center gap-3">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                <span className="font-medium">No contradictions detected across your documents.</span>
              </div>
            )}
          </div>
          
          {result.missing_evidence && result.missing_evidence.length > 0 && (
            <div>
              <h3 className="text-xl font-bold text-navy mb-4 flex items-center gap-2">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><line x1="8" y1="12" x2="16" y2="12"/></svg>
                Missing Evidence
              </h3>
              <ul className="bg-gray-50 border border-gray-200 rounded-2xl p-6 space-y-3">
                {result.missing_evidence.map((item, i) => (
                  <li key={i} className="flex items-start gap-3 text-gray-700">
                    <div className="w-1.5 h-1.5 rounded-full bg-gray-400 mt-2 shrink-0" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {result.scoring_model_note && (
            <div className="text-center pt-8 border-t border-gray-100">
              <p className="text-xs text-gray-400 font-medium tracking-wide">
                DISCLAIMER: {result.scoring_model_note}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
