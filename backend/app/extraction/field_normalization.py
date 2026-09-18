FIELD_NAME_ALIASES = {
    "claim_amount_requested": "claim_amount",
    "amount_claimed": "claim_amount",
    "total_claim_amount": "claim_amount",
    "total_billed_amount": "claim_amount",
    "invoice_amount": "claim_amount",
    "requested_amount": "claim_amount",
    "admission_date_claim_form": "admission_date",
    "date_of_admission": "admission_date",
    "date_of_discharge": "discharge_date",
    "discharge_date_summary": "discharge_date",
    "policy_no": "policy_number",
    "policy_num": "policy_number",
}

def normalize_field_name(field: str) -> str:
    """Normalizes slightly varying LLM-extracted field names into their canonical schema names."""
    field_lower = field.strip().lower()
    return FIELD_NAME_ALIASES.get(field_lower, field_lower)
