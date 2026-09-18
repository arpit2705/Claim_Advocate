from fastapi import FastAPI
from app.api.routes import router as api_router

app = FastAPI(
    title="Claim Advocate",
    description=(
        "Policy-grounded reasoning engine for insurance claim readiness (Module A) "
        "and post-rejection adjudication (Module B)."
    ),
    version="0.1.0",
)

app.include_router(api_router)

@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
