"""
Integration tests for ScoutR unified backend.

Tests Dev 1 (data layer), Dev 2 (orchestrator), and Dev 3 (tactical fit, export)
together via the FastAPI app.
"""

import pytest


# ──────────────────────────────────────────────
#  Dev 1 — Data & Backend
# ──────────────────────────────────────────────

class TestDev1Health:
    """Dev 1: System endpoints."""

    def test_health(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json().get("status") == "ok"
        assert "scoutr" in r.json().get("service", "").lower()

    def test_root(self, client):
        r = client.get("/")
        assert r.status_code == 200
        assert r.json().get("status") == "ok"


class TestDev1Search:
    """Dev 1: POST /search."""

    def test_search_returns_structure(self, client):
        r = client.post("/search", json={"position": "left-back", "max_age": 24})
        assert r.status_code == 200
        data = r.json()
        assert "candidates" in data or "status" in data


class TestDev1Comparables:
    """Dev 1: GET /comparables."""

    def test_comparables_by_target_fee(self, client):
        r = client.get("/comparables?target_fee=5.0")
        assert r.status_code == 200
        data = r.json()
        assert "comparables" in data
        assert isinstance(data["comparables"], list)

    def test_comparables_by_player_id_dev3(self, client):
        """Dev 3: /comparables?player_id=X for PDF export."""
        r = client.get("/comparables?player_id=1001")
        assert r.status_code == 200
        data = r.json()
        assert "comparables" in data


class TestDev1Player:
    """Dev 1: GET /player/{id}."""

    def test_player_404_for_unknown(self, client):
        r = client.get("/player/unknown_player_xyz_99999")
        assert r.status_code == 404

    def test_player_returns_for_golden_path_id_if_exists(self, client):
        """If ChromaDB has golden path IDs, /player/1001 should work."""
        r = client.get("/player/1001")
        if r.status_code == 200:
            data = r.json()
            assert "player_id" in data or "name" in data or "market_value" in data


# ──────────────────────────────────────────────
#  Dev 2 — Scout + Valuation Agents
# ──────────────────────────────────────────────

class TestDev2Query:
    """Dev 2: POST /query (full orchestration)."""

    GOLDEN_PATH_QUERY = (
        "Find me a left-back under 24, comfortable in a high press, "
        "contract expiring within 12 months, available for under €7M, "
        "preferably from a league with similar intensity to the Championship."
    )

    def test_query_golden_path_returns_dossiers(self, client):
        r = client.post("/query", json={"query": self.GOLDEN_PATH_QUERY})
        assert r.status_code == 200
        data = r.json()
        assert "dossiers" in data
        assert "query" in data
        dossiers = data["dossiers"]
        assert isinstance(dossiers, list)
        assert len(dossiers) >= 1

    def test_query_dossier_has_fee_range(self, client):
        r = client.post("/query", json={"query": self.GOLDEN_PATH_QUERY})
        assert r.status_code == 200
        dossiers = r.json().get("dossiers", [])
        for d in dossiers[:1]:
            assert "fee_range" in d or "player" in d


# ──────────────────────────────────────────────
#  Dev 3 — Tactical Fit + Monitoring + PDF Export
# ──────────────────────────────────────────────

class TestDev3TacticalFit:
    """Dev 3: Tactical Fit in dossiers."""

    GOLDEN_PATH_QUERY = (
        "Find me a left-back under 24, comfortable in a high press, "
        "contract expiring within 12 months, available for under €7M, "
        "preferably from a league with similar intensity to the Championship."
    )

    def test_dossier_has_tactical_fit_fields(self, client):
        r = client.post("/query", json={"query": self.GOLDEN_PATH_QUERY})
        assert r.status_code == 200
        dossiers = r.json().get("dossiers", [])
        for d in dossiers[:1]:
            assert "tactical_fit_score" in d
            assert "fit_explanation" in d
            assert "heatmap_zones" in d
            assert "formation_compatibility" in d
            # At least one should be non-null when Tactical Fit runs
            assert (
                d.get("tactical_fit_score") is not None
                or d.get("fit_explanation") is not None
                or d.get("formation_compatibility") is not None
            )


class TestDev3Export:
    """Dev 3: POST /export."""

    def test_export_returns_pdf_or_503(self, client):
        r = client.post("/export", json={"player_ids": [1001, 1002], "query": "Test"})
        assert r.status_code in (200, 503)
        if r.status_code == 200:
            assert r.headers.get("content-type", "").startswith("application/pdf")
            assert len(r.content) > 100
            assert r.content[:4] == b"%PDF"

    def test_export_with_empty_ids_uses_golden_path(self, client):
        r = client.post("/export", json={"player_ids": [], "query": "Leeds left-back"})
        assert r.status_code in (200, 503)


class TestDev3Monitoring:
    """Dev 3: Monitoring Agent (via scoutr directly, not HTTP)."""

    def test_check_watchlist_returns_alerts(self):
        from scoutr.agents.monitoring import check_watchlist
        result = check_watchlist([1001, 1002], api_base_url="http://localhost:99999")
        assert "alerts" in result
        assert isinstance(result["alerts"], list)
