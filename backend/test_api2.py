import os
import httpx

pdf_path = "dummy.pdf"
if os.path.exists(pdf_path):
    with open(pdf_path, "rb") as p, open(pdf_path, "rb") as c:
        resp = httpx.post(
            "http://127.0.0.1:8001/readiness/pipeline",
            files={"policy": (pdf_path, p, "application/pdf"), "claims": (pdf_path, c, "application/pdf")},
            timeout=120.0
        )
    print(resp.status_code)
    try:
        print(resp.json())
    except:
        print(resp.text)
else:
    print("Files not found.")
