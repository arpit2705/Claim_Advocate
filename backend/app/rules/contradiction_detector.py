"""
contradiction_detector.py — Field-by-field structured fact comparison.

Compares EvidenceFact objects across documents to find contradictions in the
same logical field. Severity is assigned deterministically by Python based on
field importance — not by the LLM.

Severity scale:
  high   — date or amount fields (material to coverage decisions)
  medium — identity fields (patient name, policy number, hospital)
  low    — supporting fields (diagnosis text, notes)
"""
from __future__ import annotations

from app.schemas.evidence import ContradictionFlag, EvidenceFact

# Fields ranked by materiality
_HIGH_SEVERITY_FIELDS = {
    "admission_date", "discharge_date", "incident_date", "claim_date",
    "claim_amount", "billed_amount", "approved_amount", "paid_amount",
    "policy_start_date", "policy_end_date",
}
_MEDIUM_SEVERITY_FIELDS = {
    "patient_name", "policy_number", "hospital_name", "insured_name",
    "member_id", "group_number",
}


def _severity_for_field(field: str) -> str:
    f = field.lower()
    if any(h in f for h in _HIGH_SEVERITY_FIELDS):
        return "high"
    if any(m in f for m in _MEDIUM_SEVERITY_FIELDS):
        return "medium"
    return "low"


def _normalise_field_key(field: str) -> str:
    """Lowercased, stripped field name for grouping."""
    return field.strip().lower()


def detect_contradictions(facts: list[EvidenceFact]) -> list[ContradictionFlag]:
    """
    Compares all EvidenceFact objects pairwise within the same logical field.

    Two facts contradict if they share the same normalised field name but have
    different values AND come from different source documents.

    Parameters
    ----------
    facts : list[EvidenceFact]
        All extracted facts across all documents for a single claim.

    Returns
    -------
    list[ContradictionFlag]
        One flag per discovered contradiction (neutral wording only).
    """
    # Group facts by normalised field name
    by_field: dict[str, list[EvidenceFact]] = {}
    for fact in facts:
        key = _normalise_field_key(fact.field)
        by_field.setdefault(key, []).append(fact)

    contradictions: list[ContradictionFlag] = []
    seen: set[frozenset] = set()  # Avoid duplicate pairs

    for field_key, group in by_field.items():
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                a, b = group[i], group[j]
                # Only flag cross-document differences
                if a.source_document == b.source_document:
                    continue
                if a.value.strip().lower() == b.value.strip().lower():
                    continue

                pair_key = frozenset({a.fact_id, b.fact_id})
                if pair_key in seen:
                    continue
                seen.add(pair_key)

                severity = _severity_for_field(field_key)
                contradictions.append(
                    ContradictionFlag(
                        field=field_key,
                        value_a=a.value,
                        source_a=a.source_document,
                        value_b=b.value,
                        source_b=b.source_document,
                        severity=severity,
                        note=(
                            f"Values are inconsistent across documents and "
                            f"require verification."
                        ),
                    )
                )

    # Sort: high → medium → low
    order = {"high": 0, "medium": 1, "low": 2}
    contradictions.sort(key=lambda c: order[c.severity])
    return contradictions
