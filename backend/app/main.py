from fastapi import FastAPI
from app.api.routes import router as api_router

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Claim Advocate",
    description=(
        "Policy-grounded reasoning engine for insurance claim readiness (Module A) "
        "and post-rejection adjudication (Module B)."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
