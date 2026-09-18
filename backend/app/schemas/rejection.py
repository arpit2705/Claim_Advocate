from pydantic import BaseModel
from app.schemas.evidence import EvidenceFact


class RejectionRecord(BaseModel):
    cited_clause_ref: str | None
    stated_reason: str
    claim_facts: list[EvidenceFact]
