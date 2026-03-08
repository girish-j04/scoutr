"""Golden Path dataset for demo fallback.

Leeds United left-back query scenario. Used when Dev 1 APIs are unavailable
or return errors, ensuring the demo always works.
"""

# Player IDs used in the Golden Path demo (Dev 1 should seed these)
GOLDEN_PATH_PLAYER_IDS = [1001, 1002, 1003]

GOLDEN_PATH_PLAYERS = [
    {
        "player_id": 1001,
        "name": "Junior Firpo",
        "club": "Real Betis",
        "league": "La Liga",
        "age": 23,
        "position": "left-back",
        "contract_expiry": "2025-06-30",
        "market_value": 4500000,
        "press_metrics": {"ppda": 9.2, "pressure_success_rate": 0.34},
        "defensive_actions_per_90": 8.1,
        "progressive_carries": 3.2,
        "xA": 0.12,
        "xG": 0.02,
    },
    {
        "player_id": 1002,
        "name": "Alfie Doughty",
        "club": "Luton Town",
        "league": "Championship",
        "age": 22,
        "position": "left-back",
        "contract_expiry": "2025-01-15",
        "market_value": 2800000,
        "press_metrics": {"ppda": 10.1, "pressure_success_rate": 0.31},
        "defensive_actions_per_90": 7.8,
        "progressive_carries": 2.8,
        "xA": 0.10,
        "xG": 0.01,
    },
    {
        "player_id": 1003,
        "name": "Rico Henry",
        "club": "Brentford",
        "league": "Championship",
        "age": 24,
        "position": "left-back",
        "contract_expiry": "2026-06-30",
        "market_value": 5500000,
        "press_metrics": {"ppda": 8.8, "pressure_success_rate": 0.36},
        "defensive_actions_per_90": 9.2,
        "progressive_carries": 3.5,
        "xA": 0.14,
        "xG": 0.03,
    },
]


def get_golden_path_player(player_id: int) -> dict | None:
    """Return golden path player by ID, or None if not found."""
    for p in GOLDEN_PATH_PLAYERS:
        if p.get("player_id") == player_id:
            return p.copy()
    return None


def get_golden_path_players() -> list[dict]:
    """Return all golden path players."""
    return [p.copy() for p in GOLDEN_PATH_PLAYERS]


def get_golden_path_player_ids() -> list[int]:
    """Return golden path player IDs for demo."""
    return GOLDEN_PATH_PLAYER_IDS.copy()
