from pydantic import BaseModel
from typing import Literal, Any


class RuleResult(BaseModel):
    rule_name: str
    status: Literal["PASS", "FAIL", "PARTIAL", "UNKNOWN", "NOT_APPLICABLE"]
    explanation: str
    # Evidence trace for grounding
    trace_details: dict[str, Any] = {}
