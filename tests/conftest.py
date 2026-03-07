"""Pytest configuration. Ensures no API keys are used during tests."""

import os

import pytest


@pytest.fixture(autouse=True)
def unset_api_keys(monkeypatch):
    """Unset GEMINI and ANTHROPIC keys so tests use fallbacks."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
