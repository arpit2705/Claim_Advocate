from pydantic import BaseModel
from typing import Literal


class EvidenceFact(BaseModel):
    fact_id: str
    field: str
    # NORMALIZED: ISO dates (YYYY-MM-DD), numeric amounts without currency symbols
    value: str
    source_document: str
    page: int | None
    confidence: float


class ContradictionFlag(BaseModel):
    field: str
    value_a: str
    source_a: str
    value_b: str
    source_b: str
    severity: Literal["low", "medium", "high"]
    # Neutral language only: "inconsistent", "requires verification"
    note: str


class SubmissionEvidence(BaseModel):
    claim_type: str
    facts: list[EvidenceFact]
    documents_provided: list[str]
