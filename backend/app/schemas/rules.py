from pydantic import BaseModel


class RuleResult(BaseModel):
    rule_name: str
    passed: bool
    explanation: str
