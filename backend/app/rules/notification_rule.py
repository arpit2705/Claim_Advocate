import re
from datetime import datetime
from app.schemas.rejection import RejectionRecord
from app.schemas.policy import Clause
from app.schemas.rules import RuleResult

def check_notification_timing(rejection: RejectionRecord, clauses: list[Clause]) -> RuleResult | None:
    stated = rejection.stated_reason.lower()
    if "notif" not in stated and "intimat" not in stated:
        return None
        
    notif_clause = next((c for c in clauses if "notification" in c.raw_text.lower() or "intimation" in c.raw_text.lower()), None)
    if not notif_clause:
        return RuleResult(
            rule_name="notification_timing", 
            status="UNKNOWN", 
            explanation="Notification clause not found in retrieved clauses."
        )
        
    # 1. Find actual delay in hours from structured facts or stated reason
    notification_delay_hours = None
    for f in rejection.claim_facts:
        if f.field == "notification_delay_hours" and f.value:
            try:
                notification_delay_hours = int(f.value)
                break
            except ValueError:
                pass
                
    if notification_delay_hours is None:
        delay_match = re.search(r'(\d+)\s*hours\s+after\s+admission', stated)
        if delay_match:
            notification_delay_hours = int(delay_match.group(1))
            
    if notification_delay_hours is None:
        return RuleResult(
            rule_name="notification_timing", 
            status="UNKNOWN", 
            explanation="Cannot establish exact notification time from rejection letter or evidence."
        )

    # 2. Extract admission and discharge to calculate discharge limit
    admission = next((f.value for f in rejection.claim_facts if f.field == "admission_date"), None)
    discharge = next((f.value for f in rejection.claim_facts if f.field == "discharge_date"), None)
    
    discharge_hours = float('inf')
    if admission and discharge:
        try:
            def _parse_date(dstr: str):
                for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
                    try:
                        return datetime.strptime(dstr, fmt)
                    except ValueError:
                        pass
                raise ValueError(f"Unknown date format {dstr}")
                
            adm_date = _parse_date(admission)
            dis_date = _parse_date(discharge)
            discharge_hours = (dis_date - adm_date).total_seconds() / 3600
        except Exception:
            pass # Continue with inf discharge_hours

    clause_text = notif_clause.raw_text.lower()
    has_discharge_cond = "before discharge" in clause_text

    # Parse thresholds from policy limit
    reimb_match = re.search(r'reimbursement[^.]*?within\s+(\d+)\s*hours', clause_text)
    cashless_match = re.search(r'cashless[^.]*?within\s+(\d+)\s*hours', clause_text)
    
    reimb_limit = int(reimb_match.group(1)) if reimb_match else None
    cashless_limit = int(cashless_match.group(1)) if cashless_match else None

    # Determine claim type
    claim_type = None
    for f in rejection.claim_facts:
        if f.field == "claim_type" and f.value:
            claim_type = f.value.lower()
    
    if not claim_type:
        if "reimbursement" in stated:
            claim_type = "reimbursement"
        elif "cashless" in stated:
            claim_type = "cashless"

    # Try to infer from facts
    if not claim_type:
        has_bills = any(f.field == "billing_items" or f.source_document.endswith("bill.pdf") for f in rejection.claim_facts)
        if has_bills:
            claim_type = "reimbursement_inferred"

    # Evaluate
    if claim_type in ("reimbursement", "cashless"):
        allowed_hours = reimb_limit if claim_type == "reimbursement" else cashless_limit
        if allowed_hours is None:
            return RuleResult(
                rule_name="notification_timing", 
                status="UNKNOWN", 
                explanation=f"Cannot parse numeric notification limit for {claim_type} claims from the policy clause."
            )
            
        deadline_hours = min(allowed_hours, discharge_hours) if has_discharge_cond else allowed_hours
            
        if notification_delay_hours <= deadline_hours:
            status = "PASS"
            expl = f"Notification delay of {notification_delay_hours} hours is within the {claim_type} limit of {allowed_hours} hours from admission."
        else:
            status = "FAIL"
            expl = f"Notification delay of {notification_delay_hours} hours exceeded the {claim_type} deadline of {deadline_hours} hours."
            
        return RuleResult(
            rule_name="notification_timing", status=status, explanation=expl,
            trace_details={"notification_delay_hours": notification_delay_hours, "allowed_hours": allowed_hours, "deadline_hours": deadline_hours}
        )
        
    else:
        # Unknown or inferred claim type, check both limits
        if not reimb_limit or not cashless_limit:
            return RuleResult(
                rule_name="notification_timing", status="UNKNOWN", 
                explanation="Cannot parse both cashless and reimbursement limits to compare against."
            )
            
        reimb_deadline = min(reimb_limit, discharge_hours) if has_discharge_cond else reimb_limit
        cashless_deadline = min(cashless_limit, discharge_hours) if has_discharge_cond else cashless_limit
        
        passes_reimb = notification_delay_hours <= reimb_deadline
        passes_cashless = notification_delay_hours <= cashless_deadline
        
        if passes_reimb and not passes_cashless:
            if claim_type == "reimbursement_inferred":
                expl = (f"{notification_delay_hours} hours exceeds the {cashless_limit}-hour cashless threshold "
                        f"but is within the {reimb_limit}-hour reimbursement threshold; claim type could not be strictly confirmed "
                        f"but available evidence (itemized bills present) suggests reimbursement, in which case notification was timely.")
                status = "PASS"
            else:
                expl = (f"{notification_delay_hours} hours exceeds the {cashless_limit}-hour cashless threshold "
                        f"but is within the {reimb_limit}-hour reimbursement threshold; claim type could not be confirmed, "
                        f"but if this is a reimbursement claim, notification was timely.")
                status = "PARTIAL"
        elif passes_reimb and passes_cashless:
            expl = f"Notification delay of {notification_delay_hours} hours is within both the cashless ({cashless_limit}h) and reimbursement ({reimb_limit}h) limits."
            status = "PASS"
        else:
            expl = f"Notification delay of {notification_delay_hours} hours exceeds both the cashless ({cashless_limit}h) and reimbursement ({reimb_limit}h) limits."
            status = "FAIL"
            
        return RuleResult(
            rule_name="notification_timing", status=status, explanation=expl,
            trace_details={"notification_delay_hours": notification_delay_hours, "reimb_limit": reimb_limit, "cashless_limit": cashless_limit}
        )
