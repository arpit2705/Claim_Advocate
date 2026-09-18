# Claim Advocate — Backend

Policy-grounded reasoning engine for insurance claim readiness (Module A) and
post-rejection adjudication (Module B).

Built for Track 2: AI-Powered Financial Journeys — 24-hour hackathon.

## Architecture

```
LLM → proposed reasoning → deterministic Python validation → final result
```

The LLM never has the final word alone. Python handles all date arithmetic,
threshold comparisons, contradiction detection, scoring, and citation checks.

## Setup

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

## Run

```bash
uvicorn app.main:app --reload
```

## Test (Phase 1)

```bash
pytest tests/test_extraction.py tests/test_retrieval.py tests/test_rules.py -v
```

## Modules

| Module | File | Purpose |
|--------|------|---------|
| Sanitizer | `extraction/sanitizer.py` | Wraps document text in delimited blocks — required for all LLM calls |
| Policy Extraction | `extraction/policy_extraction.py` | PDF → `list[Clause]` |
| Evidence Extraction | `extraction/evidence_extraction.py` | Documents → `list[EvidenceFact]` with ISO date + amount normalization |
| Embedding Index | `retrieval/embedding_index.py` | In-memory semantic index (sentence-transformers) |
| Hybrid Retrieval | `retrieval/hybrid_retrieval.py` | Exact ID + semantic search combined |
| Rule Engine | `rules/rule_engine.py` | Deterministic waiting-period / sub-limit / deadline / coverage checks |
| Contradiction Detector | `rules/contradiction_detector.py` | Cross-document field-value comparison |

## Security

All document-derived text is wrapped in `<<<DOCUMENT_DATA_BEGIN>>>` /
`<<<DOCUMENT_DATA_END>>>` delimiters before any LLM call. Prompt injection
attempts inside documents are treated as ordinary data content.

## Scoring Model Disclaimer

The readiness score is a **prototype weighted scoring model** and is not a
certified readiness determination.
