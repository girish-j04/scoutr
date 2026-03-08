"""Pytest configuration. Ensures no API keys are used during tests."""

import os
import sys
from pathlib import Path

import pytest

# Ensure backend is on path so scoutr (inside backend/) is importable
_BACKEND = Path(__file__).resolve().parent.parent / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))


@pytest.fixture(autouse=True)
def unset_api_keys(monkeypatch):
    """Unset GEMINI and ANTHROPIC keys so tests use fallbacks."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
