"""
scenarios.py — Hand-written evaluation scenarios for Module A and Module B.
"""
from app.schemas.evidence import SubmissionEvidence, EvidenceFact
from app.schemas.rejection import RejectionRecord
from app.schemas.policy import Clause

# ── Module A (Readiness) Scenarios ───────────────────────────────────────────

READINESS_SCENARIOS = [
    {
        "name": "Perfect Readiness",
        "input": SubmissionEvidence(
            claim_type="hospitalization",
            facts=[
                EvidenceFact(fact_id="1", field="admission_date", value="2024-05-01", source_document="bill", page=1, confidence=0.9),
                EvidenceFact(fact_id="2", field="claim_amount", value="50000", source_document="bill", page=1, confidence=0.9),
            ],
            documents_provided=["bill"]
        ),
        "required_fields": ["admission_date", "claim_amount"],
        "rule_inputs": [],
        "expected_min_score": 90.0,
    },
    {
        "name": "Missing Required Evidence",
        "input": SubmissionEvidence(
            claim_type="hospitalization",
            facts=[
                EvidenceFact(fact_id="1", field="claim_amount", value="50000", source_document="bill", page=1, confidence=0.9),
            ],
            documents_provided=["bill"]
        ),
        "required_fields": ["admission_date", "claim_amount"],
        "rule_inputs": [],
        "expected_max_score": 85.0,
    },
    {
        "name": "Contradictory Dates",
        "input": SubmissionEvidence(
            claim_type="hospitalization",
            facts=[
                EvidenceFact(fact_id="1", field="admission_date", value="2024-05-01", source_document="doc1", page=1, confidence=0.9),
                EvidenceFact(fact_id="2", field="admission_date", value="2024-05-10", source_document="doc2", page=1, confidence=0.9),
            ],
            documents_provided=["doc1", "doc2"]
        ),
        "required_fields": ["admission_date"],
        "rule_inputs": [],
        "expected_max_score": 90.0,
    },
    {
        "name": "Rule Failure (Late Submission)",
        "input": SubmissionEvidence(
            claim_type="hospitalization",
            facts=[
                EvidenceFact(fact_id="1", field="admission_date", value="2023-01-01", source_document="doc", page=1, confidence=0.9),
            ],
            documents_provided=["doc"]
        ),
        "required_fields": ["admission_date"],
        "rule_inputs": [
            {"rule": "deadline", "incident_date": "2023-01-01", "submission_date": "2024-01-01",
             "treatment_type": "unknown",
             "deadline_rules": [{"event": "claim_submission", "hospitalization_type": None,
                                 "reference_event": "admission", "deadline_value": 30, "deadline_unit": "days"}]}
        ],
        "expected_max_score": 60.0,
    }
]


# ── Module B (Adjudication) Scenarios ────────────────────────────────────────

# We'll use a shared set of clauses for the mock retriever
ADJUDICATION_CLAUSES = [
    Clause(clause_id="CL-EXC-1", clause_type="exclusion", raw_text="Pre-existing conditions within 24 months are not covered.", trigger_conditions=["pre-existing condition"], page_number=1),
    Clause(clause_id="CL-WAIT-1", clause_type="waiting_period", raw_text="30 day waiting period applies from policy start.", trigger_conditions=["claim within 30 days"], page_number=1),
]

ADJUDICATION_SCENARIOS = [
    {
        "name": "Valid Rejection (Pre-existing)",
        "input": RejectionRecord(
            cited_clause_ref="CL-EXC-1",
            stated_reason="Denied due to pre-existing condition treated 6 months ago.",
            claim_facts=[
                EvidenceFact(fact_id="1", field="diagnosis", value="Asthma", source_document="doc", page=1, confidence=0.9),
                EvidenceFact(fact_id="2", field="previous_treatment_date", value="2023-06-01", source_document="doc", page=1, confidence=0.9),
            ]
        ),
        "expected_verdicts": ["valid", "questionable"]
    },
    {
        "name": "Likely Misapplied (Waiting Period)",
        "input": RejectionRecord(
            cited_clause_ref="CL-WAIT-1",
            stated_reason="Denied due to 30 day waiting period.",
            claim_facts=[
                EvidenceFact(fact_id="1", field="policy_start_date", value="2020-01-01", source_document="doc", page=1, confidence=0.9),
                EvidenceFact(fact_id="2", field="admission_date", value="2024-01-01", source_document="doc", page=1, confidence=0.9),
            ]
        ),
        "expected_verdicts": ["likely_misapplied"]
    },
    {
        "name": "Insufficient Evidence",
        "input": RejectionRecord(
            cited_clause_ref="CL-EXC-1",
            stated_reason="Denied for pre-existing condition.",
            claim_facts=[
                EvidenceFact(fact_id="1", field="diagnosis", value="Unknown", source_document="doc", page=1, confidence=0.9)
            ]
        ),
        "expected_verdicts": ["insufficient_evidence"]
    },
    {
        "name": "Ungrounded Rejection (No Facts)",
        "input": RejectionRecord(
            cited_clause_ref="CL-EXC-1",
            stated_reason="Denied.",
            claim_facts=[]
        ),
        "expected_verdicts": ["insufficient_evidence"]
    },
    {
        "name": "Rule Override (Contradiction)",
        "input": RejectionRecord(
            cited_clause_ref="CL-WAIT-1",
            stated_reason="Denied due to waiting period.",
            claim_facts=[
                EvidenceFact(fact_id="1", field="policy_start_date", value="2024-01-01", source_document="doc1", page=1, confidence=0.9),
                EvidenceFact(fact_id="2", field="policy_start_date", value="2020-01-01", source_document="doc2", page=1, confidence=0.9),
                EvidenceFact(fact_id="3", field="admission_date", value="2024-01-15", source_document="doc1", page=1, confidence=0.9)
            ]
        ),
        "expected_verdicts": ["questionable", "insufficient_evidence"]
    }
]
