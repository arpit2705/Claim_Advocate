import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))
from app.extraction.evidence_extraction import extract_facts_from_pdf, extract_text_from_pdf
tmp_rej_path = os.path.abspath("backend/rejection_letter_valid.pdf")

if os.path.exists(tmp_rej_path):
    facts = extract_facts_from_pdf(tmp_rej_path, document_label="rejection_letter_valid.pdf")
    rej_text_dict = extract_text_from_pdf(tmp_rej_path)
    stated_reason = " ".join(rej_text_dict.values()).strip()[:1000]
    print("--- RAW STATED_REASON ---")
    print(stated_reason)
    print("-------------------------")
else:
    print(f"File not found: {tmp_rej_path}")
