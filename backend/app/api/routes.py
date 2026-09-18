"""
routes.py — FastAPI routes for Claim Advocate.

Thin wrapper around the Phase 1-3 modules. No business logic here.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Any

from app.schemas.policy import Clause
from app.schemas.evidence import EvidenceFact, SubmissionEvidence
from app.schemas.rejection import RejectionRecord
from app.schemas.verdict import Verdict, ClaimAdvocateResult
from app.schemas.readiness import ReadinessResult

from app.extraction.policy_extraction import extract_clauses_from_text, extract_clauses_from_pdf
from app.extraction.evidence_extraction import extract_facts_from_texts, extract_facts_from_pdf
from app.modules.readiness_engine import run_readiness_pipeline
from app.modules.adjudication_engine import run_adjudication_pipeline
from app.modules.appeal_generator import generate_appeal
from app.retrieval.embedding_index import ClauseEmbeddingIndex
from app.retrieval.hybrid_retrieval import HybridRetriever
from app.eval import eval_runner

router = APIRouter()

# Global in-memory index for API demo purposes
_clause_index = ClauseEmbeddingIndex()


# --- Request Models ---
class ExtractPolicyRequest(BaseModel):
    policy_text: Optional[str] = None
    pdf_path: Optional[str] = None

class ExtractEvidenceRequest(BaseModel):
    documents: Optional[dict[str, str]] = None
    pdf_path: Optional[str] = None
    document_label: Optional[str] = "document"

class ReadinessPipelineRequest(BaseModel):
    submission: SubmissionEvidence
    rule_inputs: list[dict] = []
    required_fields: list[str] = []

class AdjudicateRequest(BaseModel):
    rejection: RejectionRecord
    clauses: list[Clause]

class DraftAppealRequest(BaseModel):
    verdict: Verdict
    clauses: list[Clause]
    facts: list[EvidenceFact]
    rejection_reason: str
    grounded: bool

class AdjudicationPipelineRequest(BaseModel):
    rejection: RejectionRecord
    rule_inputs: list[dict] = []
    policy_clauses: list[Clause]


# --- Endpoints ---

@router.post("/extract-policy", response_model=list[Clause])
def api_extract_policy(req: ExtractPolicyRequest):
    try:
        if req.pdf_path:
            clauses = extract_clauses_from_pdf(req.pdf_path)
        elif req.policy_text:
            clauses = extract_clauses_from_text(req.policy_text)
        else:
            raise HTTPException(status_code=400, detail="Must provide policy_text or pdf_path")
        
        # Automatically update the global index
        _clause_index.build(clauses)
        return clauses
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/extract-evidence", response_model=list[EvidenceFact])
def api_extract_evidence(req: ExtractEvidenceRequest):
    try:
        if req.pdf_path:
            facts = extract_facts_from_pdf(req.pdf_path, document_label=req.document_label)
        elif req.documents:
            facts = extract_facts_from_texts(req.documents)
        else:
            raise HTTPException(status_code=400, detail="Must provide documents dict or pdf_path")
        return facts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


from fastapi import APIRouter, HTTPException, File, UploadFile
import tempfile
import os

from app.extraction.evidence_extraction import extract_text_from_pdf

@router.post("/readiness/pipeline", response_model=ReadinessResult)
def api_readiness_pipeline(
    policy: UploadFile = File(...),
    claims: list[UploadFile] = File(...)
):
    try:
        facts = []
        doc_names = []
        for claim in claims:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(claim.file.read())
                tmp_path = tmp.name
            try:
                extracted = extract_facts_from_pdf(tmp_path, document_label=claim.filename)
                facts.extend(extracted)
                doc_names.append(claim.filename)
            finally:
                os.remove(tmp_path)
                
        submission = SubmissionEvidence(
            claim_type="medical",
            facts=facts,
            documents_provided=doc_names
        )
        
        from datetime import date
        result = run_readiness_pipeline(
            submission=submission,
            rule_inputs=[
                {"rule": "waiting_period", "policy_start_date": date(2023, 1, 1), "incident_date": date(2024, 5, 1), "waiting_period_days": 30},
                {"rule": "sub_limit", "claimed_amount": 50000, "sub_limit_amount": 100000, "benefit_name": "Hospitalization"},
                {"rule": "deadline", "incident_date": date(2024, 5, 1), "submission_date": date(2024, 5, 15), "deadline_days": 90},
                {"rule": "coverage_period", "policy_start_date": date(2023, 1, 1), "policy_end_date": date(2024, 12, 31), "incident_date": date(2024, 5, 1)}
            ],
            required_fields=["admission_date", "claim_amount"]
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/adjudicate", response_model=ClaimAdvocateResult)
def api_adjudicate(req: AdjudicateRequest):
    """
    Lower level endpoint to run adjudication given explicit clauses without building a fresh index.
    """
    try:
        idx = ClauseEmbeddingIndex()
        idx.build(req.clauses)
        retriever = HybridRetriever(idx)
        
        result = run_adjudication_pipeline(
            rejection=req.rejection,
            retriever=retriever
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/draft-appeal", response_model=dict)
def api_draft_appeal(req: DraftAppealRequest):
    try:
        letter = generate_appeal(
            verdict=req.verdict,
            clauses=req.clauses,
            facts=req.facts,
            rejection_reason=req.rejection_reason,
            grounded=req.grounded
        )
        return {"appeal_letter": letter}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/adjudication/pipeline", response_model=ClaimAdvocateResult)
def api_adjudication_pipeline(
    policy: UploadFile = File(...),
    rejection: UploadFile = File(...)
):
    try:
        # Extract clauses from policy
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pol:
            tmp_pol.write(policy.file.read())
            tmp_pol_path = tmp_pol.name
        try:
            clauses = extract_clauses_from_pdf(tmp_pol_path)
        finally:
            os.remove(tmp_pol_path)
            
        # Extract facts from rejection
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_rej:
            tmp_rej.write(rejection.file.read())
            tmp_rej_path = tmp_rej.name
        try:
            facts = extract_facts_from_pdf(tmp_rej_path, document_label=rejection.filename)
            rej_text_dict = extract_text_from_pdf(tmp_rej_path)
            stated_reason = " ".join(rej_text_dict.values()).strip()[:1000]
            if not stated_reason:
                stated_reason = "See attached rejection letter."
        finally:
            os.remove(tmp_rej_path)
            
        rejection_record = RejectionRecord(
            cited_clause_ref=None,
            stated_reason=stated_reason,
            claim_facts=facts
        )
        
        idx = ClauseEmbeddingIndex()
        idx.build(clauses)
        retriever = HybridRetriever(idx)

        result = run_adjudication_pipeline(
            rejection=rejection_record,
            retriever=retriever,
            rule_inputs=[]
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/eval/run")
def api_eval_run():
    """
    Runs the eval harness and returns the captured output.
    """
    import io
    import sys
    
    old_stdout = sys.stdout
    new_stdout = io.StringIO()
    sys.stdout = new_stdout
    try:
        eval_runner.run_readiness_eval()
        eval_runner.run_adjudication_eval()
    finally:
        sys.stdout = old_stdout
        
    return {"eval_output": new_stdout.getvalue()}
