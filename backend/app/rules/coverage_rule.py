from datetime import datetime
from app.schemas.rejection import RejectionRecord
from app.schemas.policy import Clause
from app.schemas.rules import RuleResult
from app.rules.rule_engine import coverage_period_check

def check_coverage_period_auto(rejection: RejectionRecord, clauses: list[Clause]) -> RuleResult | None:
    stated = rejection.stated_reason.lower()
    
    # Check if this rule is relevant based on stated reason or retrieved clauses
    keywords = ["expired", "inception", "policy period", "coverage period", "validity"]
    is_relevant = any(kw in stated for kw in keywords)
    
    if not is_relevant:
        # Or if any of the top matched clauses is explicitly about coverage
        for c in clauses:
            if c.clause_type == "coverage" and any(kw in c.raw_text.lower() for kw in keywords):
                is_relevant = True
                break
                
    if not is_relevant:
        return None
        
    # Extract dates from facts
    def _get_date(field: str) -> datetime | None:
        val = next((f.value for f in rejection.claim_facts if f.field == field), None)
        if not val:
            return None
        for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
            try:
                return datetime.strptime(val, fmt)
            except ValueError:
                pass
        return None

    policy_start = _get_date("policy_start_date")
    policy_end = _get_date("policy_end_date")
    incident = _get_date("admission_date") or _get_date("incident_date")

    if not policy_start or not policy_end:
        return RuleResult(
            rule_name="coverage_period_check",
            status="UNKNOWN",
            explanation="Policy start date or end date missing from extracted evidence."
        )
        
    if not incident:
        return RuleResult(
            rule_name="coverage_period_check",
            status="UNKNOWN",
            explanation="Incident/admission date missing from extracted evidence."
        )
        
    # Call the deterministic engine from Module A
    return coverage_period_check(
        policy_start_date=policy_start.date(),
        policy_end_date=policy_end.date(),
        incident_date=incident.date()
    )
