"""
contradiction_detector.py - Field-by-field structured fact comparison.

Compares EvidenceFact objects across documents to find contradictions in the
same logical field. Uses deterministic logic.
"""
from __future__ import annotations
from app.schemas.evidence import ContradictionFlag, EvidenceFact
import re

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
    return field.strip().lower()

def _normalize_value(val: str) -> str:
    return val.strip().lower()

def detect_contradictions(facts: list[EvidenceFact]) -> list[ContradictionFlag]:
    by_field: dict[str, list[EvidenceFact]] = {}
    for fact in facts:
        key = _normalise_field_key(fact.field)
        by_field.setdefault(key, []).append(fact)

    contradictions: list[ContradictionFlag] = []
    seen: set[frozenset] = set()

    for field_key, group in by_field.items():
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                a, b = group[i], group[j]
                if a.source_document == b.source_document:
                    continue
                    
                pair_key = frozenset({a.fact_id, b.fact_id})
                if pair_key in seen:
                    continue
                seen.add(pair_key)
                
                val_a = _normalize_value(a.value)
                val_b = _normalize_value(b.value)

                if val_a == val_b:
                    # CONSISTENT, do not flag
                    continue
                
                # If it's a list like modifiers or billing items, differences are just additional context
                if field_key in ["illness_modifiers", "hospital_department", "doctor_qualifications", "billing_items", "procedure_modifiers"]:
                    # CONTEXT_DIFFERENCE
                    continue

                severity = _severity_for_field(field_key)
                contradictions.append(
                    ContradictionFlag(
                        field=field_key,
                        value_a=a.value,
                        source_a=a.source_document,
                        value_b=b.value,
                        source_b=b.source_document,
                        severity=severity,
                        note=f"Document A lists {field_key} as {a.value} while Document B lists {b.value}, which differ."
                    )
                )

    order = {"high": 0, "medium": 1, "low": 2}
    contradictions.sort(key=lambda c: order.get(c.severity, 3))

    from datetime import datetime
    by_doc: dict[str, dict[str, EvidenceFact]] = {}
    for fact in facts:
        key = _normalise_field_key(fact.field)
        by_doc.setdefault(fact.source_document, {})[key] = fact
    
    # 1. Chronology check
    for doc, doc_facts in by_doc.items():
        adm_fact = doc_facts.get("admission_date")
        dis_fact = doc_facts.get("discharge_date")
        if adm_fact and dis_fact:
            try:
                adm = datetime.strptime(adm_fact.value.strip(), "%Y-%m-%d").date()
                dis = datetime.strptime(dis_fact.value.strip(), "%Y-%m-%d").date()
                if dis < adm:
                    contradictions.append(
                        ContradictionFlag(
                            field="chronology",
                            value_a=adm_fact.value,
                            source_a=adm_fact.source_document,
                            value_b=dis_fact.value,
                            source_b=dis_fact.source_document,
                            severity="high",
                            note=f"Chronological impossibility: Discharge date ({dis_fact.value}) occurs before Admission date ({adm_fact.value}) in document {doc}."
                        )
                    )
            except ValueError:
                pass

    # 2. Room rent math check (cross-document or single document)
    # The user says: 8500 * 3 == 25500 -> CONSISTENT
    # Actually, we don't need to flag them if they are in different fields unless they MATEMATICALLY contradict!
    # If room_rent_per_day * room_rent_quantity_days != room_rent_total, then it's a contradiction.
    all_room_rent_per_day = [f for f in facts if f.field == "room_rent_per_day"]
    all_room_rent_quantity_days = [f for f in facts if f.field == "room_rent_quantity_days"]
    all_room_rent_total = [f for f in facts if f.field == "room_rent_total"]
    
    # If we have all three components anywhere in the documents, we can verify.
    if all_room_rent_per_day and all_room_rent_quantity_days and all_room_rent_total:
        try:
            rate = float(re.sub(r"[^\d.]", "", all_room_rent_per_day[0].value))
            days = float(re.sub(r"[^\d.]", "", all_room_rent_quantity_days[0].value))
            total = float(re.sub(r"[^\d.]", "", all_room_rent_total[0].value))
            if abs((rate * days) - total) > 1.0: # allow minor rounding
                contradictions.append(
                    ContradictionFlag(
                        field="room_rent_math",
                        value_a=str(rate * days),
                        source_a="computed",
                        value_b=str(total),
                        source_b="documents",
                        severity="high",
                        note=f"Room rent math contradiction: {rate} * {days} != {total}"
                    )
                )
        except Exception:
            pass

    contradictions.sort(key=lambda c: order.get(c.severity, 3))
    return contradictions
