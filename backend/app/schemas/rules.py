from pydantic import BaseModel, computed_field
from typing import Literal, Any


class RuleResult(BaseModel):
    rule_name: str
    status: Literal["PASS", "FAIL", "PARTIAL", "UNKNOWN", "NOT_APPLICABLE"]
    explanation: str
    # Evidence trace for grounding
    trace_details: dict[str, Any] = {}

    @computed_field
    @property
    def passed(self) -> bool:
        """Convenience boolean: True only when status is PASS."""
        return self.status == "PASS"

