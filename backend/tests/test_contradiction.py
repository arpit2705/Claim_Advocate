"""
test_contradiction.py — Phase 2A tests for contradiction_detector.py
"""
import pytest
from app.schemas.evidence import EvidenceFact
from app.rules.contradiction_detector import detect_contradictions, _severity_for_field


def test_severity_mapping():
    assert _severity_for_field("admission_date") == "high"
    assert _severity_for_field("claim_amount") == "high"
    assert _severity_for_field("patient_name") == "medium"
    assert _severity_for_field("hospital_name") == "medium"
    assert _severity_for_field("diagnosis") == "low"
    assert _severity_for_field("random_notes") == "low"


def test_detect_contradiction_high_severity():
    facts = [
        EvidenceFact(
            fact_id="f1",
            field="admission_date",
            value="2024-01-01",
            source_document="doc1.pdf",
            page=1,
            confidence=0.9
        ),
        EvidenceFact(
            fact_id="f2",
            field="admission_date",
            value="2024-01-02",
            source_document="doc2.pdf",
            page=1,
            confidence=0.9
        )
    ]
    flags = detect_contradictions(facts)
    assert len(flags) == 1
    assert flags[0].severity == "high"
    assert flags[0].field == "admission_date"
    assert "which differ" in flags[0].note.lower()


def test_no_contradiction_same_value():
    facts = [
        EvidenceFact(
            fact_id="f1",
            field="patient_name",
            value="John Doe",
            source_document="doc1.pdf",
            page=1,
            confidence=0.9
        ),
        EvidenceFact(
            fact_id="f2",
            field="patient_name",
            value="John Doe",
            source_document="doc2.pdf",
            page=1,
            confidence=0.9
        )
    ]
    assert len(detect_contradictions(facts)) == 0


def test_no_contradiction_same_document():
    facts = [
        EvidenceFact(
            fact_id="f1",
            field="diagnosis",
            value="Fever",
            source_document="doc1.pdf",
            page=1,
            confidence=0.9
        ),
        EvidenceFact(
            fact_id="f2",
            field="diagnosis",
            value="Headache",
            source_document="doc1.pdf",
            page=2,
            confidence=0.9
        )
    ]
    assert len(detect_contradictions(facts)) == 0


def test_sorting_by_severity():
    facts = [
        EvidenceFact(fact_id="f1", field="diagnosis", value="Fever", source_document="d1", page=1, confidence=0.9),
        EvidenceFact(fact_id="f2", field="diagnosis", value="Cold", source_document="d2", page=1, confidence=0.9),
        EvidenceFact(fact_id="f3", field="claim_amount", value="1000", source_document="d1", page=1, confidence=0.9),
        EvidenceFact(fact_id="f4", field="claim_amount", value="2000", source_document="d2", page=1, confidence=0.9),
        EvidenceFact(fact_id="f5", field="patient_name", value="John", source_document="d1", page=1, confidence=0.9),
        EvidenceFact(fact_id="f6", field="patient_name", value="Jon", source_document="d2", page=1, confidence=0.9),
    ]
    flags = detect_contradictions(facts)
    assert len(flags) == 3
    assert flags[0].severity == "high"
    assert flags[1].severity == "medium"
    assert flags[2].severity == "low"
