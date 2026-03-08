"""
Player Search Service.

Searches for players using the local ChromaDB vector store + SQLite financials
(merged from Dev 1), then transforms flat player dicts into nested PlayerProfile
Pydantic models for the AI agents.

Falls back to mock data when ChromaDB is empty or unavailable.
"""

import math
from datetime import datetime, date

from app.schemas import ParsedSearchCriteria, PlayerProfile, PressMetrics
from app.config import get_settings
from app.mock_data import MOCK_PLAYERS


# ──────────────────────────────────────────────
#  Data Layer → Agent Adapter
# ──────────────────────────────────────────────

def _contract_expiry_to_months(expiry_str: str | None) -> int:
    """Convert a date string like '2025-06-30' to months remaining from now."""
    if not expiry_str:
        return 12  # Default if missing

    try:
        expiry_str = expiry_str.strip()
        if len(expiry_str) == 7:  # "2025-06"
            expiry_str += "-30"
        expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
        today = date.today()
        delta = expiry_date - today
        months = max(1, delta.days // 30)  # At least 1 month
        return months
    except (ValueError, TypeError):
        return 12  # Default fallback


def _estimate_minutes_played(progressive_carries: int) -> int:
    """Estimate minutes played from total progressive carries (rough: ~3 per 90)."""
    if progressive_carries <= 0:
        return 1800  # Default ~20 matches
    estimated_90s = progressive_carries / 3.0
    return max(900, int(estimated_90s * 90))


def _raw_to_player_profile(raw: dict) -> PlayerProfile:
    """
    Transform a flat player dict (from ChromaDB + SQLite) into our nested PlayerProfile.

    Input shape (ChromaDB metadata + SQLite financials):
        player_id (int), name, club, league, age, position,
        pressure_success_rate, xA (total), xG (total),
        progressive_carries (total), contract_expiry (date str),
        market_value (float)

    Output shape:
        Nested press_metrics, per-90 stats, contract_expiry_months (int),
        press_score (0-100).
    """
    pressure_success = float(raw.get("pressure_success_rate", 0.0))
    progressive_carries_total = int(raw.get("progressive_carries", 0))
    xa_total = float(raw.get("xA", 0.0))
    xg_total = float(raw.get("xG", 0.0))
    market_value = float(raw.get("market_value", 5.0)) if raw.get("market_value") else 5.0

    # Estimate minutes for per-90 calculations
    minutes = _estimate_minutes_played(progressive_carries_total)
    nineties = max(1.0, minutes / 90.0)

    # Derive PPDA from pressure success rate (inverse relationship approximation)
    ppda = max(5.0, 20.0 - (pressure_success / 6.0)) if pressure_success > 0 else 12.0

    # Derive defensive actions from pressure data
    defensive_actions = max(3.0, pressure_success / 15.0 + 3.5)

    # Contract months
    contract_months = _contract_expiry_to_months(raw.get("contract_expiry"))

    # Press score — normalize pressure_success_rate to 0-100 scale
    press_score = min(100.0, max(0.0, pressure_success))

    # Normalize position for display
    position = str(raw.get("position", "Unknown"))
    position = position.replace("left back", "Left-Back").replace("left-back", "Left-Back")
    position = position.replace("right back", "Right-Back").replace("right-back", "Right-Back")
    position = position.replace("center back", "Centre-Back").replace("centre back", "Centre-Back")
    if position and position[0].islower():
        position = position.title()

    return PlayerProfile(
        player_id=str(raw.get("player_id", "0")),
        name=str(raw.get("name", "Unknown")),
        club=str(raw.get("club", "Unknown")),
        league=str(raw.get("league", "Unknown")),
        age=int(raw.get("age", 25)),
        position=position,
        nationality=str(raw.get("nationality", "Unknown")),
        contract_expiry_months=contract_months,
        market_value=market_value,
        press_metrics=PressMetrics(
            ppda=round(ppda, 1),
            pressure_success_rate=round(pressure_success, 1),
            defensive_actions_per_90=round(defensive_actions, 1),
        ),
        progressive_carries_per_90=round(progressive_carries_total / nineties, 1),
        xa_per_90=round(xa_total / nineties, 2),
        xg_per_90=round(xg_total / nineties, 2),
        minutes_played=minutes,
        press_score=round(press_score, 1),
    )


# ──────────────────────────────────────────────
#  Search Function
# ──────────────────────────────────────────────

async def search_players(criteria: ParsedSearchCriteria) -> list[PlayerProfile]:
    """
    Search for players matching the given criteria.
    Uses the local ChromaDB vector store + SQLite financials directly.
    Falls back to mock data if ChromaDB returns no results.
    """
    settings = get_settings()

    if settings.use_mock_data:
        return _filter_mock_players(criteria)

    # Direct local data access (merged from Dev 1)
    try:
        from app.services.chroma_service import chroma_service
        from app.services.sqlite_service import get_player_financials

        # Build query dict for ChromaDB
        query_dict = {}
        if criteria.position:
            query_dict["position"] = criteria.position
        if criteria.max_age is not None:
            query_dict["max_age"] = criteria.max_age
        if criteria.min_press_score is not None:
            query_dict["min_press_score"] = criteria.min_press_score

        # Search ChromaDB
        results = chroma_service.search_players(query_dict)

        candidates_raw = results.get("metadatas", [])
        if not candidates_raw:
            print("[!] ChromaDB returned no candidates, falling back to mock data")
            return _filter_mock_players(criteria)

        # Enrich with SQLite financials and transform into PlayerProfile
        profiles = []
        for raw in candidates_raw:
            try:
                pid = str(raw.get("player_id", ""))
                if pid:
                    financials = get_player_financials(pid)
                    if financials:
                        raw.update(financials)

                profile = _raw_to_player_profile(raw)
                profiles.append(profile)
            except Exception as e:
                print(f"[!] Failed to parse player {raw.get('name', '?')}: {e}")
                continue

        if not profiles:
            print("[!] No valid profiles after transformation, falling back to mock data")
            return _filter_mock_players(criteria)

        return profiles

    except Exception as e:
        print(f"[!] Local data search failed: {e}. Falling back to mock data.")
        return _filter_mock_players(criteria)


def _filter_mock_players(criteria: ParsedSearchCriteria) -> list[PlayerProfile]:
    """Filter mock players based on parsed search criteria."""
    results = []

    for player in MOCK_PLAYERS:
        # Position filter
        if criteria.position and criteria.position.lower() not in player.position.lower():
            continue

        # Age filter
        if criteria.max_age is not None and player.age > criteria.max_age:
            continue

        # Fee filter
        if criteria.max_fee is not None and player.market_value > criteria.max_fee:
            continue

        # Contract expiry filter
        if criteria.contract_expiry_within_months is not None:
            if player.contract_expiry_months > criteria.contract_expiry_within_months:
                continue

        # Press score filter
        if criteria.min_press_score is not None:
            if player.press_score < criteria.min_press_score:
                continue

        results.append(player)

    return results
