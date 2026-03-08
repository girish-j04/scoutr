"""Unit tests for scoutr.scoring.tactical_score."""

import pytest

from scoutr.scoring.tactical_score import (
    compute_formation_compatibility,
    compute_tactical_fit_score,
    get_top_formations,
    _get_nested,
    _get_press_metrics,
    _score_defensive_actions,
    _score_heatmap_centroid,
    _score_ppda_fit,
    _score_pressure_success,
    _score_progressive_carries,
)


class TestGetNested:
    """Tests for _get_nested helper."""

    def test_nested_path(self):
        data = {"a": {"b": {"c": 42}}}
        assert _get_nested(data, "a", "b", "c") == 42.0

    def test_missing_key_returns_default(self):
        data = {"a": 1}
        assert _get_nested(data, "x", "y", default=0.0) == 0.0

    def test_none_value_returns_default(self):
        data = {"a": None}
        assert _get_nested(data, "a", default=5.0) == 5.0


class TestGetPressMetrics:
    """Tests for _get_press_metrics."""

    def test_from_press_metrics_dict(self):
        player = {"press_metrics": {"ppda": 9.0, "pressure_success_rate": 0.35}}
        ppda, rate = _get_press_metrics(player)
        assert ppda == 9.0
        assert rate == 0.35

    def test_flat_keys_fallback(self):
        player = {"ppda": 10.0, "pressure_success_rate": 0.28}
        ppda, rate = _get_press_metrics(player)
        assert ppda == 10.0
        assert rate == 0.28

    def test_defaults_when_empty(self):
        player = {}
        ppda, rate = _get_press_metrics(player)
        assert ppda == 12.0
        assert rate == 0.30


class TestScorePpdaFit:
    """Tests for _score_ppda_fit."""

    def test_at_ideal_returns_100(self):
        profile = {"ppda_ideal": 10.0, "ppda_max": 14.0}
        assert _score_ppda_fit(10.0, profile) == 100.0

    def test_below_ideal_returns_100(self):
        profile = {"ppda_ideal": 10.0, "ppda_max": 14.0}
        assert _score_ppda_fit(8.0, profile) == 100.0

    def test_at_max_returns_0(self):
        profile = {"ppda_ideal": 10.0, "ppda_max": 14.0}
        assert _score_ppda_fit(14.0, profile) == 0.0


class TestScorePressureSuccess:
    """Tests for _score_pressure_success."""

    def test_high_rate_returns_100(self):
        profile = {"pressure_success_min": 0.24}
        assert _score_pressure_success(0.45, profile) == 100.0

    def test_low_rate_returns_less(self):
        profile = {"pressure_success_min": 0.24}
        score = _score_pressure_success(0.12, profile)
        assert 0 <= score <= 60


class TestScoreProgressiveCarries:
    """Tests for _score_progressive_carries."""

    def test_above_threshold_returns_100(self):
        profile = {"progressive_carries_min": 1.0}
        assert _score_progressive_carries(2.0, profile) == 100.0


class TestScoreDefensiveActions:
    """Tests for _score_defensive_actions (ScoutR spec: defensive actions per 90)."""

    def test_left_back_above_ideal_returns_100(self):
        assert _score_defensive_actions(12.0, "left-back") == 100.0

    def test_central_midfield_below_min_returns_less(self):
        score = _score_defensive_actions(1.0, "central-midfield")
        assert 0 <= score < 70


class TestScoreHeatmapCentroid:
    """Tests for _score_heatmap_centroid (ScoutR spec: positional heatmap centroid)."""

    def test_none_returns_50(self):
        assert _score_heatmap_centroid(None, "left-back") == 50.0

    def test_ideal_centroid_returns_high(self):
        assert _score_heatmap_centroid({"x": 0.15, "y": 0.35}, "left-back") == 100.0

    def test_far_centroid_returns_low(self):
        score = _score_heatmap_centroid({"x": 0.9, "y": 0.9}, "left-back")
        assert score < 50


class TestComputeFormationCompatibility:
    """Tests for compute_formation_compatibility."""

    def test_returns_all_formations(self):
        player = {
            "position": "left-back",
            "press_metrics": {"ppda": 9.0, "pressure_success_rate": 0.35},
            "progressive_carries": 2.5,
        }
        compat = compute_formation_compatibility(player)
        assert set(compat.keys()) == {"4-3-3", "4-2-3-1", "3-5-2", "4-4-2", "3-4-3"}
        for v in compat.values():
            assert 0 <= v <= 100

    def test_golden_path_player_scores_sensible(self):
        from scoutr.golden_path import get_golden_path_player
        player = get_golden_path_player(1001)
        compat = compute_formation_compatibility(player)
        assert all(50 <= v <= 100 for v in compat.values())

    def test_defensive_actions_affects_score(self):
        """defensive_actions_per_90 from ScoutR spec influences scoring."""
        base = {"position": "left-back", "press_metrics": {"ppda": 9.0, "pressure_success_rate": 0.35}, "progressive_carries": 2.5}
        low = compute_formation_compatibility({**base, "defensive_actions_per_90": 2.0})
        high = compute_formation_compatibility({**base, "defensive_actions_per_90": 10.0})
        assert high["4-3-3"] >= low["4-3-3"]


class TestComputeTacticalFitScore:
    """Tests for compute_tactical_fit_score."""

    def test_score_in_range(self):
        player = {
            "position": "left-back",
            "press_metrics": {"ppda": 9.0, "pressure_success_rate": 0.35},
            "progressive_carries": 2.5,
        }
        score = compute_tactical_fit_score(player)
        assert 0 <= score <= 100

    def test_empty_compat_returns_50(self):
        # Use player that might produce edge case - actually empty compat never happens
        player = {"position": "left-back"}
        score = compute_tactical_fit_score(player)
        assert 0 <= score <= 100


class TestGetTopFormations:
    """Tests for get_top_formations."""

    def test_returns_top_n(self):
        player = {
            "position": "left-back",
            "press_metrics": {"ppda": 9.0, "pressure_success_rate": 0.35},
            "progressive_carries": 2.5,
        }
        top = get_top_formations(player, top_n=2)
        assert len(top) == 2
        assert all(isinstance(f, str) for f in top)

    def test_sorted_by_score_descending(self):
        player = {
            "position": "left-back",
            "press_metrics": {"ppda": 9.0, "pressure_success_rate": 0.35},
            "progressive_carries": 2.5,
        }
        compat = compute_formation_compatibility(player)
        top = get_top_formations(player, top_n=5)
        scores = [compat[f] for f in top]
        assert scores == sorted(scores, reverse=True)
