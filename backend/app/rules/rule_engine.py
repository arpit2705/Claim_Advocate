"""
rule_engine.py — Deterministic rule checks for insurance claims.

All logic here is pure Python — no LLM involved. Checks include:
  - waiting_period_check: did the incident occur after the policy waiting period?
  - sub_limit_check: does the claimed amount exceed any applicable sub-limit?
  - deadline_check: was the claim submitted within the required deadline?
  - coverage_period_check: did the incident occur within the policy coverage window?

Each check returns a RuleResult with passed=True/False and a plain explanation.
"""
from __future__ import annotations

from datetime import date, timedelta

from app.schemas.rules import RuleResult


# ── Individual rule functions ─────────────────────────────────────────────────

def waiting_period_check(
    policy_start_date: date,
    incident_date: date,
    waiting_period_days: int,
    rule_name: str = "waiting_period_check",
) -> RuleResult:
    coverage_start = policy_start_date + timedelta(days=waiting_period_days)
    passed = incident_date >= coverage_start
    if passed:
        explanation = (
            f"Incident date {incident_date.isoformat()} is on or after "
            f"waiting period end {coverage_start.isoformat()} "
            f"(policy inception {policy_start_date.isoformat()} + {waiting_period_days}-day waiting period satisfied)."
        )
    else:
        delta = (coverage_start - incident_date).days
        explanation = (
            f"Incident date {incident_date.isoformat()} falls within the "
            f"{waiting_period_days}-day waiting period (ends {coverage_start.isoformat()}, "
            f"from inception {policy_start_date.isoformat()}) — incident is {delta} day(s) early."
        )
    return RuleResult(
        rule_name=rule_name,
        status="PASS" if passed else "FAIL",
        explanation=explanation,
        trace_details={"policy_start": policy_start_date.isoformat(), "incident_date": incident_date.isoformat(), "waiting_period_days": waiting_period_days}
    )


def sub_limit_check(
    sub_limit_amount: float,
    benefit_name: str = "benefit",
    claimed_amount: float | None = None,
    rule_name: str = "sub_limit_check",
    is_per_day: bool = False,
) -> RuleResult:
    unit = "/day" if is_per_day else ""
    if claimed_amount is None:
        return RuleResult(
            rule_name=rule_name,
            status="UNKNOWN",
            explanation=f"Cannot evaluate the {benefit_name} sub-limit because the actual amount was not provided in the claim documents. The policy limit is Rs. {sub_limit_amount:,.2f}{unit}.",
            trace_details={"policy_limit": sub_limit_amount, "is_per_day": is_per_day}
        )

    passed = claimed_amount <= sub_limit_amount
    if passed:
        explanation = (
            f"{benefit_name.capitalize()} of Rs. {claimed_amount:,.0f}{unit} is within the "
            f"Rs. {sub_limit_amount:,.0f}{unit} sub-limit."
        )
    else:
        excess = claimed_amount - sub_limit_amount
        explanation = (
            f"{benefit_name.capitalize()} of Rs. {claimed_amount:,.0f}{unit} exceeds the "
            f"Rs. {sub_limit_amount:,.0f}{unit} sub-limit by Rs. {excess:,.0f}{unit}."
        )
    return RuleResult(
        rule_name=rule_name,
        status="PASS" if passed else "FAIL",
        explanation=explanation,
        trace_details={"policy_limit": sub_limit_amount, "claimed_amount": claimed_amount, "is_per_day": is_per_day}
    )


def deadline_check(
    incident_date: date,
    treatment_type: str,
    submission_date: date | None = None,
    intimation_date: date | None = None,
    discharge_date: date | None = None,
    deadline_rules: list[dict] | None = None,
    rule_name: str = "deadline_check",
) -> RuleResult:
    if not deadline_rules:
        return RuleResult(
            rule_name=rule_name,
            status="NOT_APPLICABLE",
            explanation="No structured deadline rules found in the policy.",
            trace_details={}
        )

    # We evaluate all rules. If any fail, the check fails. If we lack info for any, it's UNKNOWN.
    statuses = []
    explanations = []

    for rule in deadline_rules:
        event = rule.get("event")
        hosp_type = rule.get("hospitalization_type")
        ref_event = rule.get("reference_event")
        d_val = rule.get("deadline_value")
        d_unit = rule.get("deadline_unit")

        # Skip if rule doesn't match hospitalization type
        if hosp_type and hosp_type.lower() != treatment_type.lower() and treatment_type.lower() != "unknown":
            continue
        
        # Determine reference date
        ref_date = incident_date if ref_event == "admission" else discharge_date
        if ref_date is None:
            statuses.append("UNKNOWN")
            explanations.append(f"Cannot evaluate {event} deadline because {ref_event} date is missing.")
            continue

        # Determine target date
        target_date = intimation_date if event == "claim_intimation" else submission_date

        deadline = ref_date + timedelta(days=d_val if d_unit == "days" else (d_val // 24))

        if target_date is None:
            statuses.append("UNKNOWN")
            # Specific semantic wording as requested
            if event == "claim_intimation" and submission_date is not None:
                explanations.append(f"Claim submission date is available, but the policy requires claim intimation within {d_val} {d_unit} of {ref_event} (for {hosp_type or 'any'} admission). A separate claim-intimation timestamp is not available.")
            else:
                explanations.append(f"Cannot evaluate {event} deadline because the actual {event} date is missing. Required within {d_val} {d_unit} of {ref_event}.")
            continue

        if target_date <= deadline:
            statuses.append("PASS")
            explanations.append(f"{event.replace('_', ' ').capitalize()} on {target_date.isoformat()} was within {d_val} {d_unit} of {ref_event} (deadline: {deadline.isoformat()}).")
        else:
            statuses.append("FAIL")
            explanations.append(f"{event.replace('_', ' ').capitalize()} on {target_date.isoformat()} missed the {d_val} {d_unit} deadline of {deadline.isoformat()} from {ref_event}.")

    if not statuses:
        return RuleResult(rule_name=rule_name, status="NOT_APPLICABLE", explanation="No applicable deadline rules for this treatment type.", trace_details={"treatment_type": treatment_type})

    if "FAIL" in statuses:
        final_status = "FAIL"
    elif "UNKNOWN" in statuses and "PASS" in statuses:
        final_status = "PARTIAL"
    elif "UNKNOWN" in statuses:
        final_status = "UNKNOWN"
    else:
        final_status = "PASS"

    return RuleResult(
        rule_name=rule_name,
        status=final_status,
        explanation=" ".join(explanations),
        trace_details={"rules_evaluated": len(statuses), "treatment_type": treatment_type}
    )


def coverage_period_check(
    policy_start_date: date,
    policy_end_date: date,
    incident_date: date,
    rule_name: str = "coverage_period_check",
) -> RuleResult:
    passed = policy_start_date <= incident_date <= policy_end_date
    if passed:
        explanation = (
            f"Incident date {incident_date.isoformat()} is within policy "
            f"coverage period {policy_start_date.isoformat()} to "
            f"{policy_end_date.isoformat()}."
        )
    else:
        if incident_date < policy_start_date:
            explanation = (
                f"Incident date {incident_date.isoformat()} is before policy "
                f"start {policy_start_date.isoformat()}."
            )
        else:
            explanation = (
                f"Incident date {incident_date.isoformat()} is after policy "
                f"expiry {policy_end_date.isoformat()}."
            )
    return RuleResult(
        rule_name=rule_name,
        status="PASS" if passed else "FAIL",
        explanation=explanation,
        trace_details={"policy_start": policy_start_date.isoformat(), "policy_end": policy_end_date.isoformat(), "incident_date": incident_date.isoformat()}
    )


# ── Batch runner ──────────────────────────────────────────────────────────────

def run_all_rules(rule_inputs: list[dict]) -> list[RuleResult]:
    """
    Runs a list of rule specifications and returns all results.

    Each dict in rule_inputs must have a key "rule" matching a known rule name,
    plus the required keyword arguments for that rule.

    Supported rule names: "waiting_period", "sub_limit", "deadline", "coverage_period".

    Parameters
    ----------
    rule_inputs : list[dict]
        List of {"rule": "<name>", **kwargs} dicts.

    Returns
    -------
    list[RuleResult]
        One RuleResult per input dict.
    """
    results: list[RuleResult] = []
    for spec in rule_inputs:
        rule = spec.get("rule", "")
        # Strip meta-keys that aren't real function params
        conflict_note: str | None = spec.get("conflict_note")
        kwargs = {k: v for k, v in spec.items() if k not in ("rule", "conflict_note")}

        if rule == "waiting_period":
            result = waiting_period_check(**kwargs)
            if conflict_note:
                result = RuleResult(
                    rule_name=result.rule_name,
                    status=result.status,
                    explanation=result.explanation + f" [Note: {conflict_note}]",
                    trace_details=result.trace_details
                )
            results.append(result)
        elif rule == "sub_limit":
            results.append(sub_limit_check(**kwargs))
        elif rule == "deadline":
            results.append(deadline_check(**kwargs))
        elif rule == "coverage_period":
            result = coverage_period_check(**kwargs)
            if conflict_note:
                result = RuleResult(
                    rule_name=result.rule_name,
                    status=result.status,
                    explanation=result.explanation + f" [Note: {conflict_note}]",
                    trace_details=result.trace_details
                )
            results.append(result)
        elif rule == "skipped":
            # Explicit "could not evaluate" result
            rule_name = kwargs.get("rule_name", "unknown_check")
            reason = kwargs.get("reason", "Insufficient data to evaluate this rule.")
            results.append(
                RuleResult(
                    rule_name=rule_name,
                    status="UNKNOWN",
                    explanation=f"Cannot evaluate: {reason}",
                    trace_details={}
                )
            )
        else:
            results.append(
                RuleResult(
                    rule_name=rule or "unknown",
                    status="FAIL",
                    explanation=f"Unknown rule: '{rule}'",
                    trace_details={}
                )
            )
    return results

