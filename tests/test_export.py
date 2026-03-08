"""Unit tests for scoutr.export.pdf_service."""

import pytest

from scoutr.export.pdf_service import (
    _build_html,
    _contract_risk,
    _get_fee_range,
    _get_player,
    generate_pdf,
    PDFKIT_AVAILABLE,
    WEASYPRINT_AVAILABLE,
)
from scoutr.golden_path import get_golden_path_player


class TestGetPlayer:
    """Tests for _get_player (uses golden path when API down)."""

    def test_returns_golden_path_when_api_unreachable(self):
        player = _get_player(1001, "http://localhost:99999")
        assert player is not None
        assert player["player_id"] == 1001


class TestGetFeeRange:
    """Tests for _get_fee_range."""

    def test_fallback_from_golden_path_player(self):
        low, mid, high = _get_fee_range(1001, "http://localhost:99999")
        assert low != "N/A"
        assert mid != "N/A"
        assert high != "N/A"
        assert "€" in low or "," in low


class TestContractRisk:
    """Tests for _contract_risk."""

    def test_none_returns_na(self):
        assert _contract_risk(None) == "N/A"

    def test_far_future_returns_green(self):
        from datetime import datetime, timezone, timedelta
        future = (datetime.now(timezone.utc) + timedelta(days=400)).strftime("%Y-%m-%d")
        assert _contract_risk(future) == "green"

    def test_near_expiry_returns_amber_or_red(self):
        from datetime import datetime, timezone, timedelta
        soon = (datetime.now(timezone.utc) + timedelta(days=90)).strftime("%Y-%m-%d")
        risk = _contract_risk(soon)
        assert risk in ("amber", "red")


class TestBuildHtml:
    """Tests for _build_html."""

    def test_contains_required_sections(self):
        players = [get_golden_path_player(1001)]
        tactical_fits = {1001: {"tactical_fit_score": 85}}
        fee_ranges = {1001: ("€3M", "€4.5M", "€6M")}
        html = _build_html("Test query", "Leeds United", players, tactical_fits, fee_ranges)
        assert "ScoutR Scouting Report" in html
        assert "Leeds United" in html
        assert "Test query" in html
        assert "Junior Firpo" in html
        assert "85" in html


class TestGeneratePdf:
    """Tests for generate_pdf. Requires pdfkit+wkhtmltopdf or weasyprint to produce bytes."""

    def _can_generate_pdf(self) -> bool:
        """Try to generate a minimal PDF to see if any backend works."""
        try:
            generate_pdf([1001], api_base_url="http://localhost:99999")
            return True
        except RuntimeError:
            return False

    def test_generates_pdf_when_lib_available(self):
        try:
            pdf = generate_pdf([1001, 1002], query="Test", api_base_url="http://localhost:99999")
        except RuntimeError:
            pytest.skip("No PDF backend available (install wkhtmltopdf or weasyprint)")
        assert isinstance(pdf, bytes)
        assert len(pdf) > 100
        assert pdf[:4] == b"%PDF"

    def test_raises_when_no_pdf_lib(self):
        """When neither pdfkit nor weasyprint works, RuntimeError is raised."""
        if self._can_generate_pdf():
            pytest.skip("PDF backend available, cannot test RuntimeError")
        with pytest.raises(RuntimeError) as exc_info:
            generate_pdf([1001], api_base_url="http://localhost:99999")
        assert "pdfkit" in str(exc_info.value).lower() or "weasyprint" in str(exc_info.value).lower()

    def test_empty_player_ids_uses_golden_path(self):
        try:
            pdf = generate_pdf([], api_base_url="http://localhost:99999")
        except RuntimeError:
            pytest.skip("No PDF backend available")
        assert isinstance(pdf, bytes)
        assert len(pdf) > 0
