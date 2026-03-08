"""Unit tests for scoutr.scoring.formations."""

import pytest

from scoutr.scoring.formations import FORMATION_PROFILES, POSITION_FORMATION_WEIGHTS


class TestFormationProfiles:
    """Tests for FORMATION_PROFILES constant."""

    def test_all_formations_present(self):
        """All five formations from spec must exist."""
        expected = {"4-3-3", "4-2-3-1", "3-5-2", "4-4-2", "3-4-3"}
        assert set(FORMATION_PROFILES.keys()) == expected

    def test_each_formation_has_required_keys(self):
        """Each formation profile has required scoring keys."""
        required = {"ppda_max", "ppda_ideal", "pressure_success_min", "progressive_carries_min"}
        for formation, profile in FORMATION_PROFILES.items():
            for key in required:
                assert key in profile, f"{formation} missing {key}"
                assert isinstance(profile[key], (int, float))

    def test_ppda_ideal_less_than_max(self):
        """PPDA ideal should be <= max for each formation."""
        for formation, profile in FORMATION_PROFILES.items():
            assert profile["ppda_ideal"] <= profile["ppda_max"], f"{formation} ppda_ideal > ppda_max"


class TestPositionFormationWeights:
    """Tests for POSITION_FORMATION_WEIGHTS."""

    def test_left_back_weights(self):
        """Left-back has weights for common formations."""
        weights = POSITION_FORMATION_WEIGHTS["left-back"]
        assert "4-3-3" in weights
        assert "3-5-2" in weights
        assert weights["4-3-3"] >= 0.9

    def test_unknown_position_handled(self):
        """Unknown position is absent; callers use .get() for default."""
        assert "unknown-position" not in POSITION_FORMATION_WEIGHTS
