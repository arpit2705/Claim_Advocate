import re
from datetime import datetime
from app.schemas.rejection import RejectionRecord
from app.schemas.policy import Clause
from app.schemas.rules import RuleResult
from app.rules.rule_engine import waiting_period_check

def check_waiting_period_auto(rejection: RejectionRecord, clauses: list[Clause]) -> RuleResult | None:
    stated = rejection.stated_reason.lower()
    
    # 1. Determine if waiting period is relevant
    keywords = ["waiting period", "wait period", "exclusion period", "pre-existing", "pre existing"]
    is_relevant = any(kw in stated for kw in keywords)
    
    matched_clause = None
    for c in clauses:
        if c.clause_type == "waiting_period" or any(kw in c.raw_text.lower() for kw in keywords):
            is_relevant = True
            matched_clause = c
            break

    if not is_relevant:
        return None

    # 2. Extract policy start and incident date from facts
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
    incident = _get_date("admission_date") or _get_date("incident_date")

    if not policy_start:
        return RuleResult(
            rule_name="waiting_period_check",
            status="UNKNOWN",
            explanation="Policy start date missing from extracted evidence."
        )
        
    if not incident:
        return RuleResult(
            rule_name="waiting_period_check",
            status="UNKNOWN",
            explanation="Incident/admission date missing from extracted evidence."
        )

    # 3. Determine waiting period days
    waiting_period_days = None
    
    # First, look at structured clause metadata if available
    if matched_clause and matched_clause.waiting_period_days:
        waiting_period_days = matched_clause.waiting_period_days
    elif matched_clause and matched_clause.day_count and matched_clause.clause_type == "waiting_period":
        waiting_period_days = matched_clause.day_count

    # If missing, try to parse from the rejection reason or clause text
    if not waiting_period_days:
        texts_to_search = [stated]
        if matched_clause:
            texts_to_search.append(matched_clause.raw_text.lower())
            
        for text in texts_to_search:
            # 24 months, 48 months
            mo_match = re.search(r'(\d+)\s*(?:month|mo)', text)
            if mo_match:
                months = int(mo_match.group(1))
                waiting_period_days = int(months * 30.416) # rough average month length
                break
            
            # 2 years, 3 years
            yr_match = re.search(r'(\d+)\s*(?:year|yr)', text)
            if yr_match:
                years = int(yr_match.group(1))
                waiting_period_days = years * 365
                break
                
            # 30 days, 90 days
            day_match = re.search(r'(\d+)\s*(?:day|d)', text)
            if day_match:
                waiting_period_days = int(day_match.group(1))
                break

    if not waiting_period_days:
        return RuleResult(
            rule_name="waiting_period_check",
            status="UNKNOWN",
            explanation="Could not determine the exact waiting period duration (days/months/years) from the rejection letter or policy clause."
        )

    # 4. Evaluate using deterministic engine
    return waiting_period_check(
        policy_start_date=policy_start.date(),
        incident_date=incident.date(),
        waiting_period_days=waiting_period_days
    )
