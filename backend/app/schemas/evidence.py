from pydantic import BaseModel, Field
from typing import Literal

# Schema A: Document Classification
class DocumentClassification(BaseModel):
    document_type: Literal[
        "claim_form", "discharge_summary", "hospital_bill", "payment_receipt",
        "prescription", "investigation_report", "identity_proof", "other"
    ]
    confidence: float

# Schema B: Evidence Extraction (Facts per document)
class DocumentFacts(BaseModel):
    policy_number: str | None = None
    patient_name: str | None = None
    claimant_name: str | None = None
    admission_date: str | None = None
    discharge_date: str | None = None
    
    # Entities
    hospital_name: str | None = None
    hospital_department: str | None = None
    doctor_name: str | None = None
    doctor_qualifications: list[str] = Field(default_factory=list)
    
    # Illness and Procedure
    core_illness: str | None = None
    illness_modifiers: list[str] = Field(default_factory=list)
    medical_procedure: str | None = None
    billing_items: list[str] = Field(default_factory=list)
    
    # Amounts
    claim_amount: float | None = None
    room_rent_per_day: float | None = None
    room_rent_quantity_days: int | None = None
    room_rent_total: float | None = None
    
    # Dates
    claim_intimation_date: str | None = None
    claim_submission_date: str | None = None
    notification_delay_hours: int | None = None
    
    treatment_type: str | None = None

class DocumentEvidence(BaseModel):
    document_type: str
    original_filename: str
    classification_confidence: float
    facts: DocumentFacts

class MultiDocumentExtraction(BaseModel):
    documents: list[DocumentEvidence]

class EvidenceFact(BaseModel):
    fact_id: str
    field: str
    # NORMALIZED: ISO dates (YYYY-MM-DD), numeric amounts without currency symbols
    value: str
    source_document: str
    page: int | None
    confidence: float

class ContradictionFlag(BaseModel):
    field: str
    value_a: str
    source_a: str
    value_b: str
    source_b: str
    severity: Literal["low", "medium", "high"]
    # Neutral language only: "inconsistent", "requires verification"
    note: str

class SubmissionEvidence(BaseModel):
    claim_type: str
    facts: list[EvidenceFact]
    documents_provided: list[str]
