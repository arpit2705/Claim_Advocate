"""
conftest.py — shared pytest fixtures for Claim Advocate backend tests.

All LLM-dependent tests are skipped automatically when GROQ_API_KEY is absent,
so the deterministic (no-LLM) tests always run in CI without credentials.
"""
import os
import pytest


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "requires_llm: mark test as requiring a live GROQ_API_KEY"
    )


@pytest.fixture(scope="session")
def groq_available() -> bool:
    return bool(os.environ.get("GROQ_API_KEY", "").strip())


@pytest.fixture(autouse=True)
def skip_if_no_llm(request, groq_available):
    """Auto-skip any test marked requires_llm when GROQ_API_KEY is missing."""
    if request.node.get_closest_marker("requires_llm") and not groq_available:
        pytest.skip("GROQ_API_KEY not set — skipping LLM-dependent test")
