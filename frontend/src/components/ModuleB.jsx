import React, { useState } from 'react';
import FileUpload from './FileUpload';
import LoadingState from './LoadingState';
import ErrorAlert from './ErrorAlert';
import VerdictBadge from './VerdictBadge';
import ClauseComparison from './ClauseComparison';
import EvidenceTrace from './EvidenceTrace';
import AppealLetter from './AppealLetter';
import RequirementCheck from './RequirementCheck';
import { checkAdjudication } from '../services/api';
import { mockAdjudicationResult, mockAdjudicationResultValid } from '../data/mockData';

export default function ModuleB() {
  const [policyFiles, setPolicyFiles] = useState([]);
  const [rejectionFiles, setRejectionFiles] = useState([]);
  const [status, setStatus] = useState('idle'); // idle | loading | success | error
  const [result, setResult] = useState(null);

  const canSubmit = policyFiles.length > 0 && rejectionFiles.length > 0;

  const handleSubmit = async () => {
    if (!canSubmit) return;
    setStatus('loading');
    
    try {
      // In a real app we'd call the API:
      // const data = await checkAdjudication(policyFiles[0], rejectionFiles[0]);
      
      // For demo, simulate API call delay and use mock data
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Toggle mock data based on file size/name for demo variety
      if (rejectionFiles[0].name.toLowerCase().includes('valid')) {
        setResult(mockAdjudicationResultValid);
      } else {
        setResult(mockAdjudicationResult);
      }
      
      setStatus('success');
    } catch (err) {
      console.error(err);
      setStatus('error');
    }
  };

  const handleReset = () => {
    setPolicyFiles([]);
    setRejectionFiles([]);
    setStatus('idle');
    setResult(null);
  };

  return (
    <div className="max-w-4xl mx-auto p-4 sm:p-6 lg:p-8 animate-fade-in" id="module-b">
      <div className="text-center mb-10">
        <h2 className="text-3xl font-bold text-navy mb-3">If You're Rejected</h2>
        <p className="text-gray-500">Upload your policy and rejection letter to verify the insurer's decision.</p>
      </div>

      {status === 'idle' && (
        <div className="space-y-8">
          <div className="bg-white p-6 sm:p-8 rounded-3xl shadow-sm border border-gray-100">
            <FileUpload 
              label="Policy Document" 
              sublabel="Upload your insurance policy PDF"
              accept=".pdf"
              multiple={false}
              files={policyFiles}
              onFilesChange={setPolicyFiles}
            />
          </div>

          <div className="bg-white p-6 sm:p-8 rounded-3xl shadow-sm border border-gray-100">
            <FileUpload 
              label="Rejection Letter" 
              sublabel="Upload the formal rejection letter from your insurer"
              accept=".pdf,.png,.jpg,.jpeg"
              multiple={false}
              files={rejectionFiles}
              onFilesChange={setRejectionFiles}
              icon={<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/><line x1="9" y1="15" x2="15" y2="15"/></svg>}
            />
          </div>

          <div className="flex justify-center pt-4">
            <button
              onClick={handleSubmit}
              disabled={!canSubmit}
              className={`px-10 py-4 rounded-full font-bold text-lg transition-all ${
                canSubmit 
                  ? 'bg-primary hover:bg-primary-dark text-white hover:shadow-lg hover:shadow-primary/30 hover:-translate-y-0.5' 
                  : 'bg-gray-200 text-gray-400 cursor-not-allowed'
              }`}
            >
              Check My Rejection
            </button>
          </div>
        </div>
      )}

      {status === 'loading' && <LoadingState message="Analyzing rejection letter..." />}

      {status === 'error' && (
        <ErrorAlert onRetry={() => setStatus('idle')} />
      )}

      {status === 'success' && result && (
        <div className="space-y-12 animate-fade-in-up">
          <div className="flex justify-between items-center mb-6">
             <h3 className="text-2xl font-bold text-navy">Rejection Analysis Complete</h3>
             <button 
                onClick={handleReset}
                className="text-sm font-semibold text-primary hover:text-primary-dark"
              >
                ← Check another
              </button>
          </div>
          
          <VerdictBadge 
            verdict={result.verdict.verdict} 
            consistencyScore={result.verdict.consistency_score} 
          />

          <div className="bg-white rounded-3xl p-8 border border-gray-200 shadow-sm">
            <h4 className="text-xl font-bold text-navy mb-4">Explanation</h4>
            <p className="text-gray-700 leading-relaxed">
              {result.explanation}
            </p>
            
            <ClauseComparison 
              matchedClauseId={result.verdict.matched_clause_id}
              matchedClauseText="The policy document specifies a 24-month waiting period for Category II conditions. The policyholder's condition (Type 2 Diabetes) is listed as Category II in Schedule A." // Mock actual clause text extraction
              insurerReason="Your claim is denied under Clause 4.2.1 due to the 48-month waiting period for pre-existing conditions." // Mock extraction from letter
              mismatchExplanation={result.verdict.mismatch_explanation}
            />
            
            <EvidenceTrace passes={result.verdict.pass_results} />
          </div>

          <div>
            <h3 className="text-xl font-bold text-navy mb-4 flex items-center gap-2">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#3281B7" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="9 11 12 14 22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>
              Policy Rules Checked
            </h3>
            <div className="grid md:grid-cols-2 gap-4">
              {result.rule_results.map((rule, i) => (
                <RequirementCheck key={i} rule={rule} index={i} />
              ))}
            </div>
          </div>
          
          {!result.grounded && (
             <div className="bg-amber-50 border border-amber-200 rounded-2xl p-6 text-center">
                <h4 className="font-bold text-amber-800 mb-2">Unable to Fully Verify</h4>
                <p className="text-amber-700 text-sm">
                  The available evidence could not fully ground this result. The analysis relied on partial information.
                </p>
             </div>
          )}

          {result.appeal_letter && (result.verdict.verdict === 'questionable' || result.verdict.verdict === 'likely_misapplied') && (
            <AppealLetter content={result.appeal_letter} />
          )}
        </div>
      )}
    </div>
  );
}
