"""Tactical scoring logic for player-fit evaluation.

Computes tactical_fit_score (0-100) and formation_compatibility per formation.
Uses PPDA, pressure success rate, defensive actions, progressive carries, etc.
"""

from typing import Any

from scoutr.scoring.formations import (
    DEFENSIVE_ACTIONS_BY_POSITION,
    FORMATION_PROFILES,
    HEATMAP_CENTROID_BY_POSITION,
    POSITION_FORMATION_WEIGHTS,
)


def _get_nested(player: dict[str, Any], *keys: str, default: float = 0.0) -> float:
    """Safely get nested or flat value from player dict."""
    val = player
    for k in keys:
        if isinstance(val, dict) and k in val:
            val = val[k]
        else:
            return default
    try:
        return float(val) if val is not None else default
    except (TypeError, ValueError):
        return default


def _get_press_metrics(player: dict[str, Any]) -> tuple[float, float]:
    """Extract PPDA and pressure success rate. Lower PPDA = more intense press."""
    press = player.get("press_metrics") or {}
    ppda = _get_nested(player, "press_metrics", "ppda", default=_get_nested(player, "ppda", default=12.0))
    if ppda == 0.0:
        ppda = 12.0
    pressure_success = _get_nested(
        player, "press_metrics", "pressure_success_rate",
        default=_get_nested(player, "pressure_success_rate", default=0.30)
    )
    return ppda, pressure_success


def _score_ppda_fit(ppda: float, profile: dict) -> float:
    """0-100: lower PPDA = better for high-press formations."""
    ideal = profile.get("ppda_ideal", 10.0)
    max_ppda = profile.get("ppda_max", 14.0)
    if ppda <= ideal:
        return 100.0
    if ppda >= max_ppda:
        return 0.0
    return max(0, 100 - (ppda - ideal) / (max_ppda - ideal) * 100)


def _score_pressure_success(rate: float, profile: dict) -> float:
    """0-100: higher pressure success = better fit."""
    min_rate = profile.get("pressure_success_min", 0.24)
    if rate >= 0.40:
        return 100.0
    if rate < min_rate:
        return max(0, rate / min_rate * 50)
    return 50 + (rate - min_rate) / (0.40 - min_rate) * 50


def _score_progressive_carries(carries: float, profile: dict) -> float:
    """0-100: progressive carries vs formation requirement."""
    min_carries = profile.get("progressive_carries_min", 1.0)
    if carries >= min_carries * 1.5:
        return 100.0
    if carries < min_carries * 0.5:
        return max(0, carries / (min_carries * 0.5) * 50)
    return 50 + (carries - min_carries * 0.5) / min_carries * 50


def _score_defensive_actions(actions: float, position: str) -> float:
    """0-100: defensive actions per 90 vs position-expected range (ScoutR spec)."""
    expected = DEFENSIVE_ACTIONS_BY_POSITION.get(
        position, (4.0, 8.0)
    )
    min_exp, ideal = expected
    if actions >= ideal:
        return 100.0
    if actions < min_exp:
        return max(0, actions / min_exp * 60)
    return 60 + (actions - min_exp) / (ideal - min_exp) * 40


def _score_heatmap_centroid(
    centroid: dict | None, position: str
) -> float:
    """0-100: proximity of positional heatmap centroid to ideal zone (ScoutR spec).

    centroid: {"x": 0.3, "y": 0.5} (normalized pitch 0-1).
    Returns 50 (neutral) if centroid not provided.
    """
    if not centroid or not isinstance(centroid, dict):
        return 50.0
    try:
        x = float(centroid.get("x", 0.5))
        y = float(centroid.get("y", 0.5))
    except (TypeError, ValueError):
        return 50.0
    ideal = HEATMAP_CENTROID_BY_POSITION.get(
        position, (0.5, 0.5)
    )
    dist = ((x - ideal[0]) ** 2 + (y - ideal[1]) ** 2) ** 0.5
    # dist 0 -> 100, dist 0.5 -> ~0
    if dist <= 0.1:
        return 100.0
    score = max(0, 100 - dist * 150)
    return score


def compute_formation_compatibility(player: dict[str, Any]) -> dict[str, float]:
    """Compute compatibility score (0-100) for each formation.

    Returns dict like {"4-3-3": 85, "4-2-3-1": 72, ...}.
    """
    ppda, pressure_success = _get_press_metrics(player)
    progressive_carries = _get_nested(player, "progressive_carries", default=1.5)
    defensive_actions = _get_nested(player, "defensive_actions_per_90", default=6.0)
    centroid = player.get("heatmap_centroid") or player.get("positional_heatmap_centroid")
    position = (player.get("position") or "central-midfield").lower().replace(" ", "-")

    pos_weights = POSITION_FORMATION_WEIGHTS.get(position, {})
    s_defensive = _score_defensive_actions(defensive_actions, position)
    s_centroid = _score_heatmap_centroid(centroid, position)

    result = {}
    for formation, profile in FORMATION_PROFILES.items():
        s_ppda = _score_ppda_fit(ppda, profile)
        s_pressure = _score_pressure_success(pressure_success, profile)
        s_carries = _score_progressive_carries(progressive_carries, profile)
        raw = (
            s_ppda * 0.30
            + s_pressure * 0.30
            + s_carries * 0.15
            + s_defensive * 0.15
            + s_centroid * 0.10
        )
        weight = pos_weights.get(formation, 1.0)
        result[formation] = min(100, round(raw * weight, 1))

    return result


def compute_tactical_fit_score(player: dict[str, Any]) -> float:
    """Compute overall tactical fit score 0-100.

    Weighted average of formation compatibilities, with 4-3-3 and 4-2-3-1
    weighted slightly higher as common formations.
    """
    compat = compute_formation_compatibility(player)
    if not compat:
        return 50.0
    weights = {"4-3-3": 1.2, "4-2-3-1": 1.1, "3-5-2": 1.0, "4-4-2": 1.0, "3-4-3": 1.0}
    total = sum(compat.get(f, 50) * weights.get(f, 1.0) for f in compat)
    denom = sum(weights.get(f, 1.0) for f in compat)
    return round(min(100, total / denom), 1)


def get_top_formations(player: dict[str, Any], top_n: int = 3) -> list[str]:
    """Return top N formations by compatibility (for formation_compatibility output)."""
    compat = compute_formation_compatibility(player)
    sorted_formations = sorted(compat.items(), key=lambda x: -x[1])
    return [f[0] for f in sorted_formations[:top_n]]
