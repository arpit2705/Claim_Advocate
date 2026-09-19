from pydantic import BaseModel
from typing import Literal
from app.schemas.rules import RuleResult
from app.schemas.evidence import ContradictionFlag


class DocumentStatus(BaseModel):
    filename: str
    document_type: str | None
    status: Literal["PROCESSING", "PROCESSED", "PROCESSING_FAILED", "UNREADABLE", "UNSUPPORTED"]
    message: str | None = None

class ScoreBreakdown(BaseModel):
    check: str
    status: str
    weight: float
    contribution: float
    reason: str | None = None


class ReadinessResult(BaseModel):
    readiness_score: float
    verification_status: Literal["FULLY_VERIFIED", "PARTIALLY_VERIFIED", "REQUIRES_REVIEW"]
    rule_results: list[RuleResult]
    contradictions: list[ContradictionFlag]
    detected_documents: list[str]
    missing_documents: list[str]
    missing_evidence: list[str]
    prioritized_fixes: list[str]
    score_breakdown: list[ScoreBreakdown]
    document_statuses: list[DocumentStatus] = []
    scoring_model_note: str = (
        "Prototype weighted scoring model — not a certified readiness determination."
    )
