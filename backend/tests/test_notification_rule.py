"""
test_notification_rule.py — Regression tests for notification timing rule.

Tests cover:
  TEST 1: Reimbursement, 36h notification, 48h limit → PASS
  TEST 2: Reimbursement, 60h notification, 48h limit → FAIL
  TEST 3: Notification time missing from rejection reason → UNKNOWN
  TEST 4: Relevant notification clause retrieved for notification-delay reason
  TEST 5: "Delay in notification" rejection reason retrieves CLAIM NOTIFICATION clause
  TEST 6: Policy has no notification clause → UNKNOWN (no hallucination)
  TEST 7: "before discharge, whichever is earlier" — deadline respects the earlier bound
"""
import pytest
from unittest.mock import MagicMock

from app.schemas.policy import Clause
from app.schemas.rejection import RejectionRecord
from app.schemas.evidence import EvidenceFact
from app.rules.notification_rule import check_notification_timing
from app.retrieval.embedding_index import ClauseEmbeddingIndex
from app.retrieval.hybrid_retrieval import HybridRetriever


# ── Shared fixtures ────────────────────────────────────────────────────────────

NOTIFICATION_CLAUSE = Clause(
    clause_id="CL-005",
    clause_type="condition",
    raw_text=(
        "CLAUSE 5. CLAIM NOTIFICATION. "
        "Cashless: Emergency hospitalization should be notified within 24 hours or before discharge, whichever is earlier. "
        "Planned hospitalization should be notified at least 72 hours before hospitalization. "
        "Reimbursement: notification should be within 48 hours of admission or before discharge, whichever is earlier. "
        "Any delay may be condoned on merit where the delay is proved to have occurred for reasons beyond the insured person's control."
    ),
    trigger_conditions=["claim notification", "intimation delay"],
    page_number=5,
)

CLAIM_FACTS_BASE = [
    EvidenceFact(fact_id="f1", field="admission_date", value="2026-06-10",
                 source_document="rejection_letter", page=1, confidence=1.0),
    EvidenceFact(fact_id="f2", field="discharge_date", value="2026-06-13",
                 source_document="rejection_letter", page=1, confidence=1.0),
]


def _make_rejection(stated_reason: str, facts=None) -> RejectionRecord:
    return RejectionRecord(
        cited_clause_ref=None,
        stated_reason=stated_reason,
        claim_facts=facts or CLAIM_FACTS_BASE,
    )


# ── TEST 1: 36h notification, 48h limit → PASS ─────────────────────────────

class TestNotificationRulePass:
    def test_reimbursement_36h_within_48h_limit(self):
        rejection = _make_rejection(
            "Claim rejected due to delay in notification of hospitalization. "
            "Notification was received 36 hours after admission. "
            "This is a reimbursement claim."
        )
        result = check_notification_timing(rejection, [NOTIFICATION_CLAUSE])
        assert result is not None, "Rule should be triggered"
        assert result.status == "PASS", (
            f"Expected PASS for 36h notification with 48h limit, got {result.status}: {result.explanation}"
        )
        assert "36" in result.explanation
        assert result.trace_details["notification_delay_hours"] == 36
        assert result.trace_details["allowed_hours"] == 48


# ── TEST 2: 60h notification, 48h limit → FAIL ─────────────────────────────

class TestNotificationRuleFail:
    def test_reimbursement_60h_exceeds_48h_limit(self):
        rejection = _make_rejection(
            "Claim rejected due to delay in notification of hospitalization. "
            "Notification was received 60 hours after admission. "
            "This is a reimbursement claim."
        )
        result = check_notification_timing(rejection, [NOTIFICATION_CLAUSE])
        assert result is not None, "Rule should be triggered"
        assert result.status == "FAIL", (
            f"Expected FAIL for 60h notification with 48h limit, got {result.status}: {result.explanation}"
        )
        assert result.trace_details["notification_delay_hours"] == 60


# ── TEST 3: Notification time missing → UNKNOWN ─────────────────────────────

class TestNotificationRuleUnknown:
    def test_unknown_when_hours_not_stated(self):
        rejection = _make_rejection(
            "Claim rejected due to delay in notification of hospitalization. "
            "Notification occurred late."  # no explicit hour count
        )
        result = check_notification_timing(rejection, [NOTIFICATION_CLAUSE])
        assert result is not None
        assert result.status == "UNKNOWN", (
            f"Expected UNKNOWN when hours not stated, got {result.status}"
        )


# ── TEST 4 & 5: Retrieval — notification clause returned for delay reason ───

RETRIEVAL_CLAUSES = [
    NOTIFICATION_CLAUSE,
    Clause(
        clause_id="CL-001",
        clause_type="exclusion",
        raw_text="Pre-existing conditions are excluded from coverage.",
        trigger_conditions=["pre-existing"],
        page_number=1,
    ),
    Clause(
        clause_id="CL-002",
        clause_type="waiting_period",
        raw_text="A mandatory 30-day waiting period applies from the policy start date.",
        trigger_conditions=["waiting period"],
        page_number=2,
    ),
]


@pytest.fixture(scope="module")
def retriever_with_notification():
    idx = ClauseEmbeddingIndex()
    idx.build(RETRIEVAL_CLAUSES)
    return HybridRetriever(idx)


class TestNotificationRetrieval:

    def test_notification_delay_retrieves_notification_clause(self, retriever_with_notification):
        """TEST 4 & 5: Querying 'Delay in notification of hospitalization' must surface CL-005."""
        query = "Delay in notification of hospitalization notification intimation 48 hours admission"
        results = retriever_with_notification.retrieve(query, top_k=3)
        clause_ids = [c.clause_id for c, _ in results]
        assert "CL-005" in clause_ids, (
            f"Expected CL-005 (notification clause) in top-3 results for notification-delay query. "
            f"Got: {clause_ids}"
        )

    def test_top_result_is_notification_clause(self, retriever_with_notification):
        """Notification clause should rank #1 for intimation delay queries."""
        query = (
            "Delay in notification of hospitalization notification intimation "
            "delay reimbursement hours admission before discharge"
        )
        results = retriever_with_notification.retrieve(query, top_k=1)
        assert len(results) == 1
        top_clause, score = results[0]
        assert top_clause.clause_id == "CL-005", (
            f"Expected CL-005 at rank 1, got {top_clause.clause_id} (score={score:.3f})"
        )


# ── TEST 6: Policy has no notification clause → UNKNOWN ─────────────────────

class TestNoNotificationClause:
    def test_unknown_when_no_notification_clause(self):
        """If no notification clause exists in policy, return UNKNOWN — no hallucination."""
        rejection = _make_rejection(
            "Notification received 36 hours after admission. This is a reimbursement claim."
        )
        non_notification_clauses = [
            Clause(
                clause_id="CL-001",
                clause_type="exclusion",
                raw_text="Pre-existing conditions are excluded.",
                trigger_conditions=["pre-existing"],
                page_number=1,
            )
        ]
        result = check_notification_timing(rejection, non_notification_clauses)
        assert result is not None
        assert result.status == "UNKNOWN", (
            f"Expected UNKNOWN when no notification clause found, got {result.status}"
        )
        # Verify it says it couldn't find the clause — NOT that it invented one
        assert "not found" in result.explanation.lower() or "cannot" in result.explanation.lower()


# ── TEST 7: "before discharge, whichever is earlier" ────────────────────────

class TestBeforeDischargeCondition:
    def test_deadline_uses_discharge_when_earlier(self):
        """
        If discharge is only 30 hours after admission, 
        and policy says 'within 48h or before discharge, whichever is earlier',
        then the actual deadline is 30h, not 48h.
        """
        # Discharge is only 30 hours after admission (2026-06-10 → 2026-06-11T06:00)
        # But we use date objects; let's make discharge = admission + 1 day = 24h gap
        facts = [
            EvidenceFact(fact_id="f1", field="admission_date", value="2026-06-10",
                         source_document="doc", page=1, confidence=1.0),
            EvidenceFact(fact_id="f2", field="discharge_date", value="2026-06-11",  # 24h gap
                         source_document="doc", page=1, confidence=1.0),
        ]
        rejection = _make_rejection(
            "Notification received 36 hours after admission. This is a reimbursement claim.",
            facts=facts,
        )
        result = check_notification_timing(rejection, [NOTIFICATION_CLAUSE])
        assert result is not None
        # Discharge is 24h after admission, which is earlier than 48h limit.
        # So deadline = 24h. 36h > 24h → FAIL.
        assert result.status == "FAIL", (
            f"Expected FAIL when discharge is 24h after admission and notification was at 36h "
            f"(before-discharge condition makes deadline 24h). Got {result.status}: {result.explanation}"
        )
        assert result.trace_details["deadline_hours"] == 24.0


# ── TEST 8: Non-notification rejection reason → rule not triggered ──────────

class TestIrrelevantRejection:
    def test_waiting_period_rejection_not_triggered(self):
        """Rule should return None for unrelated rejection reasons."""
        rejection = _make_rejection("Claim rejected: illness arose within the 30-day waiting period.")
        result = check_notification_timing(rejection, [NOTIFICATION_CLAUSE])
        assert result is None, f"Expected None for non-notification rejection, got {result}"
