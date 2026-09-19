import os
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

pdf_policy = "policy_sample.pdf"
pdf_claim = "claim_evidence_valid.pdf"

if os.path.exists(pdf_policy) and os.path.exists(pdf_claim):
    with open(pdf_policy, "rb") as p, open(pdf_claim, "rb") as c:
        resp = client.post(
            "/readiness/pipeline",
            files={"policy": (pdf_policy, p, "application/pdf"), "claims": (pdf_claim, c, "application/pdf")}
        )
    print(resp.status_code)
    import json
    print(json.dumps(resp.json().get("rule_results", []), indent=2))
else:
    print("Files not found.")
