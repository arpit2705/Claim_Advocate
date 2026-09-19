from pydantic import BaseModel
from typing import Literal, Any


class Clause(BaseModel):
    clause_id: str
    clause_type: Literal["exclusion", "sub_limit", "waiting_period", "condition", "coverage", "deadline"]
    raw_text: str
    trigger_conditions: list[str]
    page_number: int | None
    # Generic: populated for ANY clause containing an "within N days of X" requirement
    day_count: int | None = None          # numeric day count (e.g. 30)
    day_count_context: str | None = None  # event it counts from/to (e.g. "discharge", "inception date")
    # Structured deadline rules for complex intimation/submission clauses
    deadline_rules: list[dict[str, Any]] = []
    # Aliases kept for backward-compat — backed by day_count when clause_type=="waiting_period"
    waiting_period_days: int | None = None
    waiting_period_from: str | None = None
