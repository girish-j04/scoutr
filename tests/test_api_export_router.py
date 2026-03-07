"""Unit tests for scoutr.api.export_router."""

import pytest
from fastapi.testclient import TestClient

from scoutr.api.export_router import export_router, ExportRequest
from fastapi import FastAPI

app = FastAPI()
app.include_router(export_router)
client = TestClient(app)


class TestExportRequest:
    """Tests for ExportRequest model."""

    def test_defaults(self):
        req = ExportRequest(player_ids=[1, 2])
        assert req.query == ""
        assert req.club == "Leeds United"


class TestExportEndpoint:
    """Tests for POST /export endpoint."""

    def test_returns_200_with_pdf_when_generation_succeeds(self):
        """When a PDF backend works, returns 200 and PDF."""
        r = client.post("/export", json={"player_ids": [1001, 1002], "query": "Test"})
        if r.status_code == 503:
            pytest.skip("No PDF backend available (install wkhtmltopdf or weasyprint)")
        assert r.status_code == 200
        assert r.headers.get("content-type", "").startswith("application/pdf")
        assert len(r.content) > 100
        assert r.content[:4] == b"%PDF"

    def test_returns_503_or_200_when_pdf_lib_unavailable(self):
        """Returns 503 when no PDF backend, 200 when one works."""
        r = client.post("/export", json={"player_ids": [1001]})
        assert r.status_code in (200, 503)
