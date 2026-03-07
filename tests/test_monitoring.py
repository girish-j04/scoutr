"""Unit tests for scoutr.agents.monitoring.

Runs without API keys; uses golden path for player data.
"""

import pytest

from scoutr.agents.monitoring import (
    check_watchlist,
    _months_until_expiry,
    _contract_urgency_alerts,
    _mock_competitor_scout_alerts,
    _mock_club_finances_alerts,
)


class TestMonthsUntilExpiry:
    """Tests for _months_until_expiry."""

    def test_none_returns_none(self):
        assert _months_until_expiry(None) is None

    def test_empty_string_returns_none(self):
        assert _months_until_expiry("") is None

    def test_valid_iso_date(self):
        """A future date should return positive months (approximately)."""
        from datetime import datetime, timezone, timedelta
        future = (datetime.now(timezone.utc) + timedelta(days=90)).strftime("%Y-%m-%d")
        months = _months_until_expiry(future)
        assert months is not None
        assert 2 < months < 4


class TestContractUrgencyAlerts:
    """Tests for _contract_urgency_alerts."""

    def test_expired_contract_red(self):
        from datetime import datetime, timezone, timedelta
        past = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d")
        alerts = _contract_urgency_alerts(1, {"name": "Test", "contract_expiry": past})
        assert len(alerts) == 1
        assert alerts[0]["type"] == "contract_urgency"
        assert alerts[0]["severity"] == "red"

    def test_no_expiry_no_alerts(self):
        alerts = _contract_urgency_alerts(1, {"name": "Test"})
        assert alerts == []


class TestMockCompetitorScoutAlerts:
    """Tests for _mock_competitor_scout_alerts."""

    def test_returns_one_alert_for_first_player(self):
        alerts = _mock_competitor_scout_alerts([1001, 1002])
        assert len(alerts) == 1
        assert alerts[0]["type"] == "competitor_scout"
        assert "[DEMO]" in alerts[0]["message"]

    def test_empty_watchlist_no_alerts(self):
        assert _mock_competitor_scout_alerts([]) == []


class TestMockClubFinancesAlerts:
    """Tests for _mock_club_finances_alerts."""

    def test_low_value_player_gets_alert(self):
        players = [{"player_id": 1, "club": "Small Club", "market_value": 2000000}]
        alerts = _mock_club_finances_alerts([1], players)
        assert len(alerts) == 1
        assert alerts[0]["type"] == "club_finances"
        assert "Small Club" in alerts[0]["message"]


class TestCheckWatchlist:
    """Tests for check_watchlist. Uses golden path when API unreachable."""

    def test_output_schema(self):
        result = check_watchlist([1001, 1002], api_base_url="http://localhost:99999")
        assert "alerts" in result
        assert isinstance(result["alerts"], list)

    def test_contract_alerts_present_for_golden_path(self):
        result = check_watchlist([1001, 1002, 1003], api_base_url="http://localhost:99999")
        types = {a["type"] for a in result["alerts"]}
        assert "contract_urgency" in types or "competitor_scout" in types

    def test_each_alert_has_required_fields(self):
        result = check_watchlist([1001], api_base_url="http://localhost:99999")
        for a in result["alerts"]:
            assert "player_id" in a
            assert "type" in a
            assert "severity" in a
            assert "message" in a
            assert "timestamp" in a
