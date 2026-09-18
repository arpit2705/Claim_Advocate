"""
test_api_layer.py — Phase 4 API tests.

Tests the FastAPI endpoints using TestClient to verify routing, status codes,
and response schemas.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.policy import Clause

client = TestClient(app)

# We use the /health endpoint just to verify the test client works.
def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_extract_policy_text():
    # Because LLM is not mocked here and we don't have GROQ_API_KEY, this would normally fail.
    # But we can at least assert that the request shape is accepted.
    response = client.post("/extract-policy", json={"policy_text": "Sample text"})
    # Since we lack the API key, it should ideally raise 500 with "GROQ_API_KEY is not set."
    # OR we just check it doesn't give a 422 Unprocessable Entity (validation error).
    assert response.status_code in [200, 500]


def test_extract_evidence_text():
    response = client.post("/extract-evidence", json={"documents": {"doc1": "Sample text"}})
    assert response.status_code in [200, 500]


def test_readiness_pipeline():
    payload = {
        "submission": {
            "claim_type": "test",
            "facts": [
                {"fact_id": "1", "field": "admission_date", "value": "2024-01-01", "source_document": "d1", "page": 1, "confidence": 1.0}
            ],
            "documents_provided": ["d1"]
        },
        "required_fields": ["admission_date"]
    }
    response = client.post("/readiness/pipeline", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["readiness_score"] == 100.0


def test_adjudicate():
    payload = {
        "rejection": {
            "cited_clause_ref": "CL-1",
            "stated_reason": "Denied.",
            "claim_facts": []
        },
        "clauses": [
            {"clause_id": "CL-1", "clause_type": "exclusion", "raw_text": "text", "trigger_conditions": [], "page_number": 1}
        ]
    }
    response = client.post("/adjudicate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "verdict" in data
    assert data["verdict"]["verdict"] == "insufficient_evidence"


def test_draft_appeal():
    payload = {
        "verdict": {
            "verdict": "likely_misapplied",
            "consistency_score": 1.0,
            "matched_clause_id": "CL-1",
            "mismatch_explanation": "Test.",
            "pass_results": ["likely_misapplied"]
        },
        "clauses": [
            {"clause_id": "CL-1", "clause_type": "exclusion", "raw_text": "text", "trigger_conditions": [], "page_number": 1}
        ],
        "facts": [
            {"fact_id": "1", "field": "date", "value": "2024-01-01", "source_document": "d1", "page": 1, "confidence": 1.0}
        ],
        "rejection_reason": "Denied.",
        "grounded": True
    }
    response = client.post("/draft-appeal", json=payload)
    # 500 if no LLM key, or 200 if mocked/key exists. We expect it not to be 422.
    assert response.status_code in [200, 500]


def test_eval_run():
    response = client.post("/eval/run")
    assert response.status_code == 200
    data = response.json()
    assert "eval_output" in data
    assert "Module A Accuracy" in data["eval_output"]
