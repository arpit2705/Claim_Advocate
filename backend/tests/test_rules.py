"""
test_rules.py — Phase 1 tests for rule_engine.py

All tests are deterministic — no LLM involved.
Tests cover: waiting_period_check, sub_limit_check, deadline_check,
             coverage_period_check, and the batch run_all_rules runner.
"""
import pytest
from datetime import date

from app.rules.rule_engine import (
    waiting_period_check,
    sub_limit_check,
    deadline_check,
    coverage_period_check,
    run_all_rules,
)
from app.schemas.rules import RuleResult


# ── waiting_period_check ──────────────────────────────────────────────────────

class TestWaitingPeriodCheck:

    def test_incident_after_waiting_period_passes(self):
        result = waiting_period_check(
            policy_start_date=date(2024, 1, 1),
            incident_date=date(2024, 2, 1),   # 31 days after start
            waiting_period_days=30,
        )
        assert result.passed is True
        assert "satisfied" in result.explanation.lower()

    def test_incident_exactly_on_coverage_start_passes(self):
        result = waiting_period_check(
            policy_start_date=date(2024, 1, 1),
            incident_date=date(2024, 1, 31),  # exactly day 30
            waiting_period_days=30,
        )
        assert result.passed is True

    def test_incident_within_waiting_period_fails(self):
        result = waiting_period_check(
            policy_start_date=date(2024, 1, 1),
            incident_date=date(2024, 1, 15),  # only 14 days in
            waiting_period_days=30,
        )
        assert result.passed is False
        assert "waiting period" in result.explanation.lower()

    def test_incident_day_before_coverage_fails(self):
        result = waiting_period_check(
            policy_start_date=date(2024, 1, 1),
            incident_date=date(2024, 1, 30),  # day 29 — one day short
            waiting_period_days=30,
        )
        assert result.passed is False

    def test_zero_waiting_period_always_passes(self):
        result = waiting_period_check(
            policy_start_date=date(2024, 1, 1),
            incident_date=date(2024, 1, 1),
            waiting_period_days=0,
        )
        assert result.passed is True

    def test_returns_rule_result_instance(self):
        result = waiting_period_check(
            policy_start_date=date(2024, 1, 1),
            incident_date=date(2024, 3, 1),
            waiting_period_days=90,
        )
        assert isinstance(result, RuleResult)
        assert result.rule_name == "waiting_period_check"

    def test_custom_rule_name(self):
        result = waiting_period_check(
            policy_start_date=date(2024, 1, 1),
            incident_date=date(2024, 6, 1),
            waiting_period_days=30,
            rule_name="custom_waiting_check",
        )
        assert result.rule_name == "custom_waiting_check"

    def test_long_waiting_period_fails_early_claim(self):
        """24-month waiting period for pre-existing conditions."""
        result = waiting_period_check(
            policy_start_date=date(2022, 1, 1),
            incident_date=date(2023, 6, 1),   # ~18 months in — still in window
            waiting_period_days=730,           # 2 years
        )
        assert result.passed is False

    def test_long_waiting_period_passes_after_two_years(self):
        result = waiting_period_check(
            policy_start_date=date(2022, 1, 1),
            incident_date=date(2024, 2, 1),   # > 2 years later
            waiting_period_days=730,
        )
        assert result.passed is True


# ── sub_limit_check ───────────────────────────────────────────────────────────

class TestSubLimitCheck:

    def test_within_limit_passes(self):
        result = sub_limit_check(
            claimed_amount=3000.0,
            sub_limit_amount=5000.0,
            benefit_name="room_rent",
        )
        assert result.passed is True

    def test_exactly_at_limit_passes(self):
        result = sub_limit_check(
            claimed_amount=5000.0,
            sub_limit_amount=5000.0,
        )
        assert result.passed is True

    def test_exceeds_limit_fails(self):
        result = sub_limit_check(
            claimed_amount=7500.0,
            sub_limit_amount=5000.0,
        )
        assert result.passed is False
        assert "exceeds" in result.explanation.lower()

    def test_explanation_contains_amounts(self):
        result = sub_limit_check(
            claimed_amount=6000.0,
            sub_limit_amount=5000.0,
        )
        assert "6000" in result.explanation
        assert "5000" in result.explanation


# ── deadline_check ────────────────────────────────────────────────────────────

class TestDeadlineCheck:

    def test_on_time_submission_passes(self):
        result = deadline_check(
            incident_date=date(2024, 3, 1),
            submission_date=date(2024, 3, 25),  # 24 days later
            deadline_days=30,
        )
        assert result.passed is True

    def test_exactly_on_deadline_passes(self):
        result = deadline_check(
            incident_date=date(2024, 3, 1),
            submission_date=date(2024, 3, 31),  # exactly 30 days
            deadline_days=30,
        )
        assert result.passed is True

    def test_late_submission_fails(self):
        result = deadline_check(
            incident_date=date(2024, 3, 1),
            submission_date=date(2024, 5, 1),   # 61 days later
            deadline_days=30,
        )
        assert result.passed is False
        assert "past the" in result.explanation.lower() or "overdue" in result.explanation.lower() or "day" in result.explanation.lower()


# ── coverage_period_check ─────────────────────────────────────────────────────

class TestCoveragePeriodCheck:

    def test_incident_within_policy_period_passes(self):
        result = coverage_period_check(
            policy_start_date=date(2024, 1, 1),
            policy_end_date=date(2024, 12, 31),
            incident_date=date(2024, 6, 15),
        )
        assert result.passed is True

    def test_incident_before_policy_start_fails(self):
        result = coverage_period_check(
            policy_start_date=date(2024, 1, 1),
            policy_end_date=date(2024, 12, 31),
            incident_date=date(2023, 12, 31),
        )
        assert result.passed is False
        assert "before" in result.explanation.lower()

    def test_incident_after_policy_expiry_fails(self):
        result = coverage_period_check(
            policy_start_date=date(2024, 1, 1),
            policy_end_date=date(2024, 12, 31),
            incident_date=date(2025, 1, 1),
        )
        assert result.passed is False
        assert "after" in result.explanation.lower() or "expiry" in result.explanation.lower()


# ── run_all_rules (batch runner) ──────────────────────────────────────────────

class TestRunAllRules:

    def test_batch_waiting_period(self):
        results = run_all_rules([
            {
                "rule": "waiting_period",
                "policy_start_date": date(2024, 1, 1),
                "incident_date": date(2024, 4, 1),
                "waiting_period_days": 30,
            }
        ])
        assert len(results) == 1
        assert results[0].passed is True

    def test_batch_mixed_rules(self):
        results = run_all_rules([
            {
                "rule": "waiting_period",
                "policy_start_date": date(2024, 1, 1),
                "incident_date": date(2024, 1, 10),
                "waiting_period_days": 30,
            },
            {
                "rule": "sub_limit",
                "claimed_amount": 3000.0,
                "sub_limit_amount": 5000.0,
            },
        ])
        assert len(results) == 2
        assert results[0].passed is False   # waiting period not met
        assert results[1].passed is True    # within sub-limit

    def test_unknown_rule_returns_failed(self):
        results = run_all_rules([{"rule": "nonexistent_rule"}])
        assert len(results) == 1
        assert results[0].passed is False
        assert "unknown" in results[0].explanation.lower()
