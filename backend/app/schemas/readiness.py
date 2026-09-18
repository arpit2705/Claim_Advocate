from pydantic import BaseModel
from app.schemas.rules import RuleResult
from app.schemas.evidence import ContradictionFlag


class ReadinessResult(BaseModel):
    readiness_score: float
    rule_results: list[RuleResult]
    contradictions: list[ContradictionFlag]
    missing_evidence: list[str]
    prioritized_fixes: list[str]
    grounded: bool
    scoring_model_note: str = (
        "Prototype weighted scoring model — not a certified readiness determination."
    )
