"""Pytest fixtures for integration tests."""

import os
import sys
from pathlib import Path

import pytest

# Ensure backend is on path when running integration tests
_BACKEND = Path(__file__).resolve().parent.parent.parent / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))


@pytest.fixture(scope="module")
def client():
    """FastAPI TestClient for the unified backend app."""
    pytest.importorskip("sse_starlette")
    from fastapi.testclient import TestClient

    # Unset API keys so Tactical Fit uses fallback (no external calls)
    os.environ.pop("GEMINI_API_KEY", None)
    os.environ.pop("ANTHROPIC_API_KEY", None)

    from app.main import app
    return TestClient(app)
