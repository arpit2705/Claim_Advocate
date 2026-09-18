from pydantic import BaseModel
from typing import Literal


class Clause(BaseModel):
    clause_id: str
    clause_type: Literal["exclusion", "sub_limit", "waiting_period", "condition", "coverage"]
    raw_text: str
    trigger_conditions: list[str]
    page_number: int | None
