import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))
from app.modules.readiness_engine import run_readiness_pipeline
from app.schemas.evidence import SubmissionEvidence, EvidenceFact

submission = SubmissionEvidence(
    claim_type="hospitalization",
    facts=[
        EvidenceFact(fact_id="1", field="admission_date", value="2024-05-01", source_document="bill", page=1, confidence=0.9),
        EvidenceFact(fact_id="2", field="claim_amount", value="50000", source_document="bill", page=1, confidence=0.9),
    ],
    documents_provided=["bill"]
)
result = run_readiness_pipeline(submission=submission, rule_inputs=[], required_fields=["admission_date", "claim_amount"])
print("--- BACKEND DIAGNOSTIC ---")
print(f"rule_results length: {len(result.rule_results)}")
print(f"grounded: {result.grounded}")
print(f"scoring_model_note: {result.scoring_model_note}")
print(f"contradictions length: {len(result.contradictions)}")
