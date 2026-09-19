from datetime import datetime
from app.schemas.rejection import RejectionRecord
from app.schemas.policy import Clause
from app.schemas.rules import RuleResult
from app.rules.rule_engine import deadline_check

def check_deadline_auto(rejection: RejectionRecord, clauses: list[Clause]) -> RuleResult | None:
    stated = rejection.stated_reason.lower()
    
    # 1. Determine if deadline is relevant (late submission, delay in filing, etc)
    keywords = ["late", "delay", "deadline", "submission", "time limit", "submitted after"]
    is_relevant = any(kw in stated for kw in keywords)
    
    matched_clause = None
    for c in clauses:
        if c.clause_type == "deadline" or any(kw in c.raw_text.lower() for kw in keywords):
            is_relevant = True
            matched_clause = c
            break

    # Exclude intimation/notification which is handled by notification_rule
    if "notification" in stated or "intimation" in stated:
        # If it specifically talks about notification, let notification_rule handle it
        # unless it ALSO mentions submission.
        if "submission" not in stated and "filing" not in stated:
            is_relevant = False

    if not is_relevant:
        return None

    # 2. Need structured deadline rules from the clause
    if not matched_clause or not matched_clause.deadline_rules:
        # We can try to infer if it's a simple deadline (e.g. 30 days) but the engine relies on deadline_rules
        if matched_clause and matched_clause.day_count:
            # Fake a simple submission rule if one isn't cleanly parsed
            day_count = matched_clause.day_count
            context = matched_clause.day_count_context or "discharge"
            deadline_rules = [{
                "event": "claim_submission",
                "hospitalization_type": "any",
                "reference_event": "admission" if "admission" in context.lower() else "discharge",
                "deadline_value": day_count,
                "deadline_unit": "days"
            }]
        else:
            return RuleResult(
                rule_name="deadline_check",
                status="UNKNOWN",
                explanation="No structured deadline rules (deadline_rules) found in the retrieved policy clause to compare against."
            )
    else:
        deadline_rules = matched_clause.deadline_rules

    # 3. Extract dates from facts
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

    incident = _get_date("admission_date") or _get_date("incident_date")
    discharge = _get_date("discharge_date")
    submission = _get_date("claim_submission_date")
    intimation = _get_date("claim_intimation_date")
    
    # Try to infer treatment type
    treatment_type = "unknown"
    for f in rejection.claim_facts:
        if f.field == "treatment_type" and f.value:
            treatment_type = f.value.lower()
            break
            
    if treatment_type == "unknown":
        if "reimbursement" in stated:
            treatment_type = "reimbursement"
        elif "cashless" in stated:
            treatment_type = "cashless"
            
    if not incident:
        return RuleResult(
            rule_name="deadline_check",
            status="UNKNOWN",
            explanation="Incident/admission date missing from extracted evidence."
        )

    # 4. Evaluate using deterministic engine
    return deadline_check(
        incident_date=incident.date(),
        treatment_type=treatment_type,
        submission_date=submission.date() if submission else None,
        intimation_date=intimation.date() if intimation else None,
        discharge_date=discharge.date() if discharge else None,
        deadline_rules=deadline_rules
    )
