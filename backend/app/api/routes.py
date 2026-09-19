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

from app.extraction.policy_extraction import extract_clauses_from_text, extract_clauses_from_pdf, extract_policy_metadata
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
            _, facts = extract_facts_from_pdf(req.pdf_path, document_label=req.document_label)
        elif req.documents:
            _, facts = extract_facts_from_texts(req.documents)
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
        doc_statuses = []
        seen_labels: dict[str, int] = {}  # track how many times each filename appeared

        for claim in claims:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(claim.file.read())
                tmp_path = tmp.name

            # Guarantee a unique source_document label even if two files share a name
            raw_label = claim.filename or f"document_{len(doc_names) + 1}"
            seen_labels[raw_label] = seen_labels.get(raw_label, 0) + 1
            label = raw_label if seen_labels[raw_label] == 1 else f"{raw_label} (copy {seen_labels[raw_label]})"

            try:
                doc_type, extracted = extract_facts_from_pdf(tmp_path, document_label=label)
                facts.extend(extracted)
                doc_names.append(doc_type)
                doc_statuses.append({
                    "filename": raw_label,
                    "document_type": doc_type,
                    "status": "PROCESSED",
                    "message": "Extracted successfully"
                })
            except ValueError as ve:
                import logging
                logging.getLogger(__name__).error(f"Document processing failed filename={raw_label} stage=extraction exception_type=ValueError exception_message={str(ve)}")
                # Check for specific unreadable PDF issue
                if "empty content" in str(ve).lower():
                    status = "UNREADABLE"
                    msg = "We couldn't read text from this document. It may be an image-only PDF."
                else:
                    status = "PROCESSING_FAILED"
                    msg = "We couldn't process this document."
                doc_statuses.append({
                    "filename": raw_label,
                    "document_type": None,
                    "status": status,
                    "message": msg
                })
            except Exception as e:
                import logging
                logging.getLogger(__name__).error(f"Document processing failed filename={raw_label} stage=extraction exception_type={type(e).__name__} exception_message={str(e)}")
                doc_statuses.append({
                    "filename": raw_label,
                    "document_type": None,
                    "status": "PROCESSING_FAILED",
                    "message": "We couldn't process this document. Please upload it again."
                })
            finally:
                os.remove(tmp_path)
                
        submission = SubmissionEvidence(
            # KNOWN SCOPE LIMITATION: For this hackathon, we only process medical claims.
            claim_type="medical",
            facts=facts,
            documents_provided=doc_names
        )
        
        # Extract clauses and metadata from policy
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pol:
            tmp_pol.write(policy.file.read())
            tmp_pol_path = tmp_pol.name
        try:
            clauses = extract_clauses_from_pdf(tmp_pol_path)
            # Deterministic regex extraction of policy-level numeric facts.
            # We do NOT use extract_facts_from_pdf here because the claim-evidence
            # LLM prompt would confuse sub-limit mentions in the policy text with
            # fields like sum_insured.
            policy_meta = extract_policy_metadata(tmp_pol_path)
        finally:
            os.remove(tmp_pol_path)

        # Build dynamic rule inputs
        from datetime import date, datetime
        import re
        import logging
        _log = logging.getLogger(__name__)

        def parse_date(d_str: str) -> date | None:
            if not d_str: return None
            try:
                return datetime.strptime(d_str, "%Y-%m-%d").date()
            except ValueError:
                return None

        # Claim facts: build fact_dict using ranked-source resolution.
        # When the same field appears in multiple documents, prefer the source
        # higher in this list (clinical records > administrative forms):
        #   1. discharge_summary  (authoritative clinical record)
        #   2. hospital_bill / hospitalization_record (itemized, specific)
        #   3. claim_form  (self-reported, prone to errors)
        # Within the same rank tier, higher LLM confidence wins.
        # The FULL facts list is kept untouched for detect_contradictions.
        _SOURCE_RANK_KEYWORDS = [
            ("discharge_summary", 0),
            ("discharge summary",  0),
            ("hospitalization_record", 1),
            ("hospital_bill",      1),
            ("hospital_record",    1),
            ("claim_form",         2),
            ("claim form",         2),
        ]

        def _source_rank(src: str) -> int:
            """Lower = higher authority. Unknown sources get rank 99."""
            s = src.lower()
            for kw, rank in _SOURCE_RANK_KEYWORDS:
                if kw in s:
                    return rank
            return 99

        fact_dict: dict[str, str]   = {}
        fact_source: dict[str, str]  = {}
        fact_rank:   dict[str, int]  = {}
        fact_conf:   dict[str, float] = {}

        for f in facts:
            key  = f.field.lower()
            rank = _source_rank(f.source_document)
            prev_rank = fact_rank.get(key, 999)
            prev_conf = fact_conf.get(key, -1.0)
            # Accept if: better rank, or same rank with higher confidence
            if rank < prev_rank or (rank == prev_rank and f.confidence > prev_conf):
                fact_dict[key]   = f.value
                fact_source[key] = f.source_document
                fact_rank[key]   = rank
                fact_conf[key]   = f.confidence

        # Build per-field value list for diagnostics and _conflict_note()
        from collections import defaultdict
        _field_values: dict[str, list[tuple[str, str]]] = defaultdict(list)
        for f in facts:
            _field_values[f.field.lower()].append((f.value, f.source_document))

        # ── STEP 1 DIAGNOSTIC: all admission_date facts with source_document ──
        _adm_entries = _field_values.get("admission_date", [])
        _log.info(
            f"[STEP 1 DIAG] admission_date facts across all documents "
            f"({len(_adm_entries)} total): "
            + (", ".join(f"'{v}' from '{src}'" for v, src in _adm_entries)
               if _adm_entries else "(none)")
        )
        _log.info(
            f"[STEP 1 DIAG] chosen admission_date='{fact_dict.get('admission_date')}' "
            f"from '{fact_source.get('admission_date')}' "
            f"(rank={fact_rank.get('admission_date')}, conf={fact_conf.get('admission_date')})"
        )

        # Log all multi-source conflicts
        for field, entries in _field_values.items():
            if len(entries) > 1 and len({v for v, _ in entries}) > 1:
                _log.info(
                    f"[DIAG-CONFLICT] field='{field}': "
                    + ", ".join(f"'{v}' ({src})" for v, src in entries)
                    + f" → chose '{fact_dict[field]}' from '{fact_source[field]}'"
                )

        # Policy-level metadata comes exclusively from policy_meta (deterministic regex)
        sum_insured: float | None = policy_meta.get("sum_insured")
        policy_start = parse_date(policy_meta.get("policy_start_date"))
        policy_end = parse_date(policy_meta.get("policy_end_date"))

        _log.info(
            f"Policy metadata extracted — sum_insured: {sum_insured}, "
            f"policy_start: {policy_start}, policy_end: {policy_end}"
        )

        admission_date = parse_date(fact_dict.get("admission_date"))
        discharge_date = parse_date(fact_dict.get("discharge_date"))

        # Build a conflict note for any date field that has multiple values across sources.
        # Used to annotate rule-check explanations when they operate on a contested value.
        def _conflict_note(field: str) -> str | None:
            """Returns a brief note if multiple source docs disagree on this field's value."""
            entries = _field_values.get(field.lower(), [])
            unique_vals = list(dict.fromkeys(v for v, _ in entries))  # ordered dedup
            if len(unique_vals) > 1:
                parts = [f"'{v}' ({src})" for v, src in entries]
                chosen_src = fact_source.get(field.lower(), "unknown source")
                return (
                    f"Using {chosen_src} value; conflicting values exist: "
                    + ", ".join(parts)
                    + ". See Contradictions section."
                )
            return None

        admission_conflict_note = _conflict_note("admission_date")
        if admission_conflict_note:
            _log.info(f"[CONFLICT] admission_date: {admission_conflict_note}")

        # ── Numeric validation gate (amount fields ONLY) ───────────────────────
        def _to_float(raw: str | None, field: str) -> float | None:
            """Strips currency symbols, validates the result is a real number."""
            if not raw:
                return None
            cleaned = re.sub(r'[^\d.]', '', raw)
            try:
                val = float(cleaned)
                return val
            except ValueError:
                _log.warning(
                    f"Numeric validation failed for field '{field}': "
                    f"'{raw}' → '{cleaned}' is not a usable number. Skipping."
                )
                return None

        claim_amount = _to_float(fact_dict.get("claim_amount"), "claim_amount")
        room_rent_per_day = _to_float(fact_dict.get("room_rent_per_day"), "room_rent_per_day")

        # Submission date from claim documents
        submission_date = parse_date(fact_dict.get("claim_submission_date"))

        # ── STEP 1 DIAGNOSTIC: point (b) — values as checks will see them ───
        _log.info(
            f"[DIAG (b)] Values reaching rule checks: "
            f"admission_date={admission_date}, discharge_date={discharge_date}, "
            f"policy_start={policy_start}, policy_end={policy_end}, "
            f"submission_date={submission_date}, "
            f"claim_amount={claim_amount}, room_rent_per_day={room_rent_per_day}, "
            f"sum_insured={sum_insured}"
        )

        dynamic_rule_inputs = []
        required_fields = ["admission_date", "claim_amount", "claim_submission_date"]

        # ── 1. waiting_period_check ──────────────────────────────────────────
        # Find the first clause EXPLICITLY typed as waiting_period and read its day_count.
        # Using clause_type as the discriminator (not keyword search) so we don't
        # accidentally pick up deadline clauses that also mention days.
        waiting_days_from_clause = None
        for c in clauses:
            if c.clause_type == "waiting_period":
                # Prefer structured day_count; waiting_period_days is the alias
                candidate = c.waiting_period_days or c.day_count
                if candidate is not None:
                    waiting_days_from_clause = candidate
                    _log.info(
                        f"[WP] waiting_period_days={waiting_days_from_clause} from clause "
                        f"{c.clause_id} (context: {c.day_count_context!r})"
                    )
                    break

        if admission_date and policy_start and waiting_days_from_clause is not None:
            wp_entry: dict = {
                "rule": "waiting_period",
                "policy_start_date": policy_start,
                "incident_date": admission_date,
                "waiting_period_days": waiting_days_from_clause,
            }
            if admission_conflict_note:
                wp_entry["conflict_note"] = admission_conflict_note
            dynamic_rule_inputs.append(wp_entry)
        else:
            missing_inputs = []
            if not admission_date:               missing_inputs.append("admission_date")
            if not policy_start:                 missing_inputs.append("policy_start_date (from policy PDF)")
            if waiting_days_from_clause is None: missing_inputs.append("waiting_period clause with day count")
            dynamic_rule_inputs.append({
                "rule": "skipped",
                "rule_name": "waiting_period_check",
                "reason": f"Cannot evaluate — missing: {', '.join(missing_inputs)}",
            })

        # ── 2. sub_limit_check ───────────────────────────────────────────────
        room_rent_total = _to_float(fact_dict.get("room_rent_total"), "room_rent_total")
        # If room_rent_per_day is already extracted by LLM, use it directly.
        # Otherwise, calculate it deterministically from room_rent_total / LOS.
        if room_rent_per_day is None and room_rent_total is not None:
            if admission_date and discharge_date:
                los_days = max(1, (discharge_date - admission_date).days)
                computed_rate = room_rent_total / los_days
                if 100 <= computed_rate <= 100000:
                    room_rent_per_day = computed_rate
                else:
                    _log.warning(
                        f"Suspicious room rent rate: Rs. {computed_rate}/day "
                        f"(total {room_rent_total} / {los_days} days) — skipping sub-limit check."
                    )
            else:
                if not discharge_date:
                    required_fields.append("discharge_date")

        sub_limit_amount_rupees = None
        for c in clauses:
            if c.clause_type == "sub_limit":
                m_pct = re.search(
                    r'(\d+(?:\.\d+)?)\s*%\s*(?:of\s+)?(?:the\s+)?(?:sum\s+insured|SI)',
                    c.raw_text, re.IGNORECASE
                )
                m_fixed = re.search(r'(?:Rs\.?|INR|₹)\s*([\d,]+)', c.raw_text, re.IGNORECASE)
                if m_pct and sum_insured is not None:
                    sub_limit_amount_rupees = (float(m_pct.group(1)) / 100.0) * sum_insured
                    break
                elif m_fixed:
                    sub_limit_amount_rupees = float(m_fixed.group(1).replace(',', ''))
                    break

        if sub_limit_amount_rupees is not None:
            dynamic_rule_inputs.append({
                "rule": "sub_limit",
                "claimed_amount": room_rent_per_day,
                "sub_limit_amount": sub_limit_amount_rupees,
                "benefit_name": "Room Rent",
                "is_per_day": True,
            })
        else:
            required_fields.append("room_rent_per_day")
            dynamic_rule_inputs.append({
                "rule": "skipped",
                "rule_name": "sub_limit_check",
                "reason": "Cannot evaluate — missing: sub_limit clause amount in policy",
            })

        # ── 3. deadline_check ────────────────────────────────────────────────
        deadline_rules = []
        for c in clauses:
            if c.deadline_rules:
                deadline_rules.extend(c.deadline_rules)

        treatment_type = fact_dict.get("treatment_type", "unknown")
        intimation_date = parse_date(fact_dict.get("claim_intimation_date"))

        # We pass everything we have to deadline_check and let it handle missing data
        # based on the structured rules (e.g. returning UNKNOWN for intimation if missing).
        dynamic_rule_inputs.append({
            "rule": "deadline",
            "incident_date": admission_date,
            "treatment_type": treatment_type,
            "submission_date": submission_date,
            "intimation_date": intimation_date,
            "discharge_date": discharge_date,
            "deadline_rules": deadline_rules,
        })

        # ── 4. coverage_period_check ─────────────────────────────────────────
        if policy_start and policy_end and admission_date:
            cp_entry: dict = {
                "rule": "coverage_period",
                "policy_start_date": policy_start,
                "policy_end_date": policy_end,
                "incident_date": admission_date,
            }
            if admission_conflict_note:
                cp_entry["conflict_note"] = admission_conflict_note
            dynamic_rule_inputs.append(cp_entry)
        else:
            missing_inputs = []
            if not policy_start:    missing_inputs.append("policy_start_date (from policy PDF)")
            if not policy_end:      missing_inputs.append("policy_end_date (from policy PDF)")
            if not admission_date:  missing_inputs.append("admission_date")
            dynamic_rule_inputs.append({
                "rule": "skipped",
                "rule_name": "coverage_period_check",
                "reason": f"Cannot evaluate — missing: {', '.join(missing_inputs)}",
            })

        _log.info(
            f"[STEP 1 DIAG] rule_inputs count: {len(dynamic_rule_inputs)} | "
            f"checks: {[r.get('rule_name', r.get('rule')) for r in dynamic_rule_inputs]}"
        )

        result = run_readiness_pipeline(
            submission=submission,
            rule_inputs=dynamic_rule_inputs,
            required_fields=required_fields
        )

        # ── STEP 4: Safety guard ─────────────────────────────────────────────
        EXPECTED_RULE_COUNT = 4
        if len(result.rule_results) < EXPECTED_RULE_COUNT:
            _log.warning(
                f"[SAFETY] Only {len(result.rule_results)} rule_results returned "
                f"(expected {EXPECTED_RULE_COUNT}). Names: "
                f"{[r.rule_name for r in result.rule_results]}"
            )

        result.document_statuses = doc_statuses
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
            _, facts = extract_facts_from_pdf(tmp_rej_path, document_label=rejection.filename)
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
