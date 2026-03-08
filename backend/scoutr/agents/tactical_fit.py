"""Tactical Fit Agent.

Fetches player stats via /player/{id}, computes tactical fit score and formation
compatibility, generates plain-English explanation via Gemini (or Claude fallback).
"""

import os
from typing import Any

import httpx

from scoutr.golden_path import get_golden_path_player
from scoutr.scoring.tactical_score import (
    compute_formation_compatibility,
    compute_tactical_fit_score,
    get_top_formations,
)


# Default heatmap zones inferred from position (simplified for demo)
POSITION_HEATMAP_ZONES = {
    "left-back": ["left-flank", "left-third", "defensive-third"],
    "right-back": ["right-flank", "right-third", "defensive-third"],
    "centre-back": ["centre", "defensive-third", "penalty-area"],
    "defensive-midfield": ["centre", "defensive-third", "middle-third"],
    "central-midfield": ["centre", "middle-third", "attacking-third"],
    "attacking-midfield": ["centre", "attacking-third", "middle-third"],
    "winger": ["left-flank", "right-flank", "attacking-third"],
    "forward": ["attacking-third", "centre", "penalty-area"],
}


def _get_player(
    player_id: int,
    api_base_url: str = "http://localhost:8000",
) -> dict[str, Any] | None:
    """Fetch player from Dev 1 API, or fall back to golden path."""
    url = f"{api_base_url.rstrip('/')}/player/{player_id}"
    try:
        with httpx.Client(timeout=10.0) as client:
            r = client.get(url)
            if r.status_code == 200:
                return r.json()
    except Exception:
        pass
    return get_golden_path_player(player_id)


def _infer_heatmap_zones(player: dict[str, Any]) -> list[str]:
    """Infer heatmap zones from position or player data."""
    zones = player.get("heatmap_zones")
    if zones and isinstance(zones, list):
        return zones[:5]
    pos = (player.get("position") or "central-midfield").lower().replace(" ", "-")
    return POSITION_HEATMAP_ZONES.get(pos, ["centre", "middle-third"])


def _generate_fit_explanation(
    player: dict[str, Any],
    tactical_fit_score: float,
    formation_compatibility: dict[str, float],
    heatmap_zones: list[str],
) -> str:
    """Generate plain-English fit explanation via Gemini."""
    gemini_key = os.environ.get("GEMINI_API_KEY")

    if not gemini_key:
        return (
            f"{player.get('name', 'Player')} scores {tactical_fit_score}/100 for tactical fit. "
            f"Best formations: {', '.join(get_top_formations(player, 3))}. "
            f"Primary zones: {', '.join(heatmap_zones)}."
        )

    compat_str = ", ".join(f"{f}: {s}" for f, s in sorted(formation_compatibility.items(), key=lambda x: -x[1]))
    prompt = f"""You are a football scout. In 2-3 sentences, explain why this player fits (or doesn't fit) a high-pressing system.

Player: {player.get('name')} ({player.get('position')}), {player.get('club')}
Tactical fit score: {tactical_fit_score}/100
Formation compatibility: {compat_str}
Heatmap zones: {', '.join(heatmap_zones)}
Pressing metrics: {player.get('press_metrics', {})}
Progressive carries: {player.get('progressive_carries', 'N/A')}

Write a concise, plain-English explanation for a sporting director."""

    if gemini_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(prompt)
            text = response.text.strip() if response.text else ""
            return text if text else _fallback_explanation(player, tactical_fit_score)
        except Exception:
            return _fallback_explanation(player, tactical_fit_score)


def _fallback_explanation(player: dict[str, Any], score: float) -> str:
    """Fallback when Claude is unavailable."""
    top = get_top_formations(player, 3)
    return (
        f"{player.get('name', 'Player')} offers a tactical fit of {score}/100. "
        f"Best suited to {', '.join(top)}. Suitable for high-press systems if pressing metrics align."
    )


def evaluate_tactical_fit(
    player_id: int,
    api_base_url: str = "http://localhost:8000",
    use_claude: bool = True,
) -> dict[str, Any]:
    """Evaluate tactical fit for a player. Returns schema for Dev 2 and Dev 4.

    Output schema:
        tactical_fit_score: 0-100
        fit_explanation: plain English text
        heatmap_zones: list of zone names
        formation_compatibility: list of best formations (e.g. ["4-3-3", "4-2-3-1"])
    """
    player = _get_player(player_id, api_base_url)
    if not player:
        return {
            "tactical_fit_score": 0,
            "fit_explanation": f"Player {player_id} not found.",
            "heatmap_zones": [],
            "formation_compatibility": [],
        }

    tactical_fit_score = compute_tactical_fit_score(player)
    formation_scores = compute_formation_compatibility(player)
    formation_compatibility = get_top_formations(player, top_n=3)
    heatmap_zones = _infer_heatmap_zones(player)

    if use_claude and (os.environ.get("GEMINI_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")):
        fit_explanation = _generate_fit_explanation(
            player, tactical_fit_score, formation_scores, heatmap_zones
        )
    else:
        fit_explanation = _fallback_explanation(player, tactical_fit_score)

    return {
        "tactical_fit_score": tactical_fit_score,
        "fit_explanation": fit_explanation,
        "heatmap_zones": heatmap_zones,
        "formation_compatibility": formation_compatibility,
    }
