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
    """
    Checks whether the incident occurred after the mandatory waiting period.

    Parameters
    ----------
    policy_start_date : date
        The date the policy became active.
    incident_date : date
        The date of the insured event.
    waiting_period_days : int
        Number of days from policy start before coverage begins.
    rule_name : str
        Label for the returned RuleResult.

    Returns
    -------
    RuleResult
        passed=True if incident_date >= policy_start_date + waiting_period_days.
    """
    coverage_start = policy_start_date + timedelta(days=waiting_period_days)
    passed = incident_date >= coverage_start
    if passed:
        explanation = (
            f"Incident date {incident_date.isoformat()} is on or after "
            f"coverage start {coverage_start.isoformat()} "
            f"({waiting_period_days}-day waiting period satisfied)."
        )
    else:
        delta = (coverage_start - incident_date).days
        explanation = (
            f"Incident date {incident_date.isoformat()} falls within the "
            f"{waiting_period_days}-day waiting period. Coverage began "
            f"{coverage_start.isoformat()} — incident is {delta} day(s) early."
        )
    return RuleResult(rule_name=rule_name, passed=passed, explanation=explanation)


def sub_limit_check(
    claimed_amount: float,
    sub_limit_amount: float,
    benefit_name: str = "benefit",
    rule_name: str = "sub_limit_check",
) -> RuleResult:
    """
    Checks whether the claimed amount is within the applicable sub-limit.

    Parameters
    ----------
    claimed_amount : float
        The amount being claimed.
    sub_limit_amount : float
        The maximum payable under the sub-limit clause.
    benefit_name : str
        Human-readable name of the benefit (for the explanation).
    rule_name : str
        Label for the returned RuleResult.

    Returns
    -------
    RuleResult
        passed=True if claimed_amount <= sub_limit_amount.
    """
    passed = claimed_amount <= sub_limit_amount
    if passed:
        explanation = (
            f"Claimed amount {claimed_amount:.2f} is within the "
            f"{benefit_name} sub-limit of {sub_limit_amount:.2f}."
        )
    else:
        excess = claimed_amount - sub_limit_amount
        explanation = (
            f"Claimed amount {claimed_amount:.2f} exceeds the "
            f"{benefit_name} sub-limit of {sub_limit_amount:.2f} "
            f"by {excess:.2f}."
        )
    return RuleResult(rule_name=rule_name, passed=passed, explanation=explanation)


def deadline_check(
    incident_date: date,
    submission_date: date,
    deadline_days: int,
    rule_name: str = "deadline_check",
) -> RuleResult:
    """
    Checks whether the claim was submitted within the required deadline.

    Parameters
    ----------
    incident_date : date
        The date the insured event occurred.
    submission_date : date
        The date the claim was filed.
    deadline_days : int
        Number of days from incident within which the claim must be submitted.
    rule_name : str
        Label for the returned RuleResult.

    Returns
    -------
    RuleResult
        passed=True if submission_date <= incident_date + deadline_days.
    """
    deadline = incident_date + timedelta(days=deadline_days)
    passed = submission_date <= deadline
    if passed:
        explanation = (
            f"Claim submitted on {submission_date.isoformat()}, within the "
            f"{deadline_days}-day deadline (deadline: {deadline.isoformat()})."
        )
    else:
        overdue = (submission_date - deadline).days
        explanation = (
            f"Claim submitted on {submission_date.isoformat()} is {overdue} "
            f"day(s) past the {deadline_days}-day deadline "
            f"(deadline was {deadline.isoformat()})."
        )
    return RuleResult(rule_name=rule_name, passed=passed, explanation=explanation)


def coverage_period_check(
    policy_start_date: date,
    policy_end_date: date,
    incident_date: date,
    rule_name: str = "coverage_period_check",
) -> RuleResult:
    """
    Checks whether the incident occurred within the policy coverage window.

    Parameters
    ----------
    policy_start_date : date
        Policy effective date.
    policy_end_date : date
        Policy expiry date.
    incident_date : date
        The date the insured event occurred.
    rule_name : str
        Label for the returned RuleResult.

    Returns
    -------
    RuleResult
        passed=True if policy_start_date <= incident_date <= policy_end_date.
    """
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
    return RuleResult(rule_name=rule_name, passed=passed, explanation=explanation)


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
        kwargs = {k: v for k, v in spec.items() if k != "rule"}
        if rule == "waiting_period":
            results.append(waiting_period_check(**kwargs))
        elif rule == "sub_limit":
            results.append(sub_limit_check(**kwargs))
        elif rule == "deadline":
            results.append(deadline_check(**kwargs))
        elif rule == "coverage_period":
            results.append(coverage_period_check(**kwargs))
        else:
            results.append(
                RuleResult(
                    rule_name=rule or "unknown",
                    passed=False,
                    explanation=f"Unknown rule: '{rule}'",
                )
            )
    return results
