"""Unit tests for scoutr.agents.tactical_fit.

Runs without API keys (conftest unsets them); uses fallback explanations and golden path.
"""

from scoutr.agents.tactical_fit import (
    POSITION_HEATMAP_ZONES,
    evaluate_tactical_fit,
    _fallback_explanation,
    _infer_heatmap_zones,
)


class TestInferHeatmapZones:
    """Tests for _infer_heatmap_zones."""

    def test_from_position(self):
        player = {"position": "left-back"}
        zones = _infer_heatmap_zones(player)
        assert zones == ["left-flank", "left-third", "defensive-third"]

    def test_from_explicit_heatmap_zones(self):
        player = {"heatmap_zones": ["zone_a", "zone_b"]}
        zones = _infer_heatmap_zones(player)
        assert zones == ["zone_a", "zone_b"]

    def test_default_position(self):
        player = {}
        zones = _infer_heatmap_zones(player)
        assert "centre" in zones and "middle-third" in zones
        assert len(zones) >= 2


class TestFallbackExplanation:
    """Tests for _fallback_explanation."""

    def test_contains_name_and_score(self):
        player = {"name": "Test Player", "position": "left-back"}
        from scoutr.scoring.tactical_score import get_top_formations
        top = get_top_formations(player, 3)
        text = _fallback_explanation(player, 85.0)
        assert "Test Player" in text
        assert "85" in text
        assert all(f in text for f in top)


class TestEvaluateTacticalFit:
    """Tests for evaluate_tactical_fit. No API keys; uses golden path."""

    def test_output_schema(self):
        """Output must match contract: tactical_fit_score, fit_explanation, heatmap_zones, formation_compatibility."""
        result = evaluate_tactical_fit(1001, use_claude=False)
        assert "tactical_fit_score" in result
        assert "fit_explanation" in result
        assert "heatmap_zones" in result
        assert "formation_compatibility" in result

    def test_tactical_fit_score_in_range(self):
        result = evaluate_tactical_fit(1001, use_claude=False)
        assert 0 <= result["tactical_fit_score"] <= 100

    def test_fit_explanation_non_empty(self):
        result = evaluate_tactical_fit(1001, use_claude=False)
        assert len(result["fit_explanation"]) > 0

    def test_formation_compatibility_list(self):
        result = evaluate_tactical_fit(1001, use_claude=False)
        assert isinstance(result["formation_compatibility"], list)
        assert len(result["formation_compatibility"]) <= 5

    def test_heatmap_zones_non_empty(self):
        result = evaluate_tactical_fit(1001, use_claude=False)
        assert len(result["heatmap_zones"]) > 0

    def test_unknown_player_returns_zero_score(self):
        result = evaluate_tactical_fit(99999, use_claude=False)
        assert result["tactical_fit_score"] == 0
        assert "not found" in result["fit_explanation"].lower()
        assert result["formation_compatibility"] == []
        assert result["heatmap_zones"] == []

    def test_uses_golden_path_when_api_unreachable(self):
        """When API is down, falls back to golden path (no real API call)."""
        result = evaluate_tactical_fit(1001, api_base_url="http://localhost:99999", use_claude=False)
        assert result["tactical_fit_score"] > 0
        assert "Junior Firpo" in result["fit_explanation"] or "Firpo" in result["fit_explanation"]
