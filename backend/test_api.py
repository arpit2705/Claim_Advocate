import os
import httpx
from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font('Arial', size=12)
pdf.cell(200, 10, txt='Dummy PDF for testing 30 day waiting period and 50000 claim amount', ln=1)
pdf.output('dummy.pdf')

pdf_path = "dummy.pdf"
if os.path.exists(pdf_path):
    with open(pdf_path, "rb") as p, open(pdf_path, "rb") as c:
        resp = httpx.post(
            "http://localhost:8000/readiness/pipeline",
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
