from pydantic import BaseModel, Field
from typing import Literal, Optional

from app.schemas.policy import Clause
from app.schemas.evidence import EvidenceFact

class Verdict(BaseModel):
    verdict: Literal["valid", "questionable", "likely_misapplied", "insufficient_evidence"]
    # Agreement rate across passes — not a probability measure
    consistency_score: float
    matched_clause_id: str | None
    mismatch_explanation: str
    pass_results: list[str]


class ClaimAdvocateResult(BaseModel):
    verdict: Verdict
    contradictions: list
    rule_results: list
    grounded: bool
    explanation: str
    appeal_letter: str | None
    matched_clause: Optional[Clause] = None
    referenced_facts: list[EvidenceFact] = Field(default_factory=list)
