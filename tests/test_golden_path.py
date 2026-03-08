"""Unit tests for scoutr.golden_path."""

import pytest

from scoutr.golden_path import (
    GOLDEN_PATH_PLAYER_IDS,
    GOLDEN_PATH_PLAYERS,
    get_golden_path_player,
    get_golden_path_players,
    get_golden_path_player_ids,
)


class TestGoldenPathConstants:
    """Tests for golden path constants."""

    def test_player_ids_list(self):
        assert GOLDEN_PATH_PLAYER_IDS == [1001, 1002, 1003]

    def test_players_have_required_fields(self):
        required = {"player_id", "name", "club", "position", "contract_expiry", "market_value"}
        for p in GOLDEN_PATH_PLAYERS:
            for key in required:
                assert key in p, f"Player missing {key}"


class TestGetGoldenPathPlayer:
    """Tests for get_golden_path_player."""

    def test_returns_player_by_id(self):
        player = get_golden_path_player(1001)
        assert player is not None
        assert player["player_id"] == 1001
        assert player["name"] == "Junior Firpo"

    def test_returns_copy_not_reference(self):
        p1 = get_golden_path_player(1001)
        p2 = get_golden_path_player(1001)
        assert p1 is not p2
        p1["name"] = "Modified"
        assert p2["name"] == "Junior Firpo"

    def test_returns_none_for_unknown_id(self):
        assert get_golden_path_player(99999) is None


class TestGetGoldenPathPlayers:
    """Tests for get_golden_path_players."""

    def test_returns_all_players(self):
        players = get_golden_path_players()
        assert len(players) == 3

    def test_returns_copies(self):
        players = get_golden_path_players()
        assert players[0] is not GOLDEN_PATH_PLAYERS[0]


class TestGetGoldenPathPlayerIds:
    """Tests for get_golden_path_player_ids."""

    def test_returns_copy_of_ids(self):
        ids = get_golden_path_player_ids()
        assert ids == [1001, 1002, 1003]
        ids.append(9999)
        assert 9999 not in GOLDEN_PATH_PLAYER_IDS
