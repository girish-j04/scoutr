"""
Comparables Service.

Uses the local CSV service (merged from Dev 1) to get similar historical transfers.
Falls back to mock data when CSV data is unavailable.
Includes an adapter to transform CSV-row dicts into ComparableTransfer models.
"""

from app.schemas import ComparableTransfer
from app.config import get_settings
from app.mock_data import MOCK_COMPARABLES


# ──────────────────────────────────────────────
#  CSV Row → ComparableTransfer Adapter
# ──────────────────────────────────────────────

def _csv_to_comparable(raw: dict) -> ComparableTransfer:
    """
    Transform a CSV-row dict into our ComparableTransfer model.

    CSV shape (from transfermarkt.csv):
        player_name, from_club, to_club, fee_m (str), season (e.g. "22/23")

    Our shape:
        player_name, from_club, to_club, fee_millions (float),
        transfer_year (int), age_at_transfer (int), position (str)
    """
    # Extract transfer year from season string like "22/23" → 2023
    season = str(raw.get("season", "23/24"))
    try:
        year_suffix = season.split("/")[1] if "/" in season else season[-2:]
        year_int = int(year_suffix)
        transfer_year = 2000 + year_int if year_int < 100 else year_int
    except (ValueError, IndexError):
        transfer_year = 2024

    # Fee
    try:
        fee = float(raw.get("fee_m", 0.0))
    except (ValueError, TypeError):
        fee = 0.0

    return ComparableTransfer(
        player_name=str(raw.get("player_name", "Unknown")),
        from_club=str(raw.get("from_club", "Unknown")),
        to_club=str(raw.get("to_club", "Unknown")),
        fee_millions=fee,
        transfer_year=transfer_year,
        age_at_transfer=int(raw.get("age_at_transfer", 23)),
        position=str(raw.get("position", "Left-Back")),
    )


# ──────────────────────────────────────────────
#  Comparables Function
# ──────────────────────────────────────────────

async def get_comparables(
    position: str,
    target_fee: float,
    age: int,
    limit: int = 5,
) -> list[ComparableTransfer]:
    """
    Get comparable historical transfers for fee estimation.
    Uses the local CSV data directly (merged from Dev 1).
    Falls back to mock data if CSV is unavailable.
    """
    settings = get_settings()

    if settings.use_mock_data:
        return _filter_mock_comparables(position, target_fee, age, limit)

    # Direct local CSV access (merged from Dev 1)
    try:
        from app.services.csv_service import get_comparables as csv_get_comparables

        raw_comps = csv_get_comparables(target_fee, limit=limit)
        if not raw_comps:
            return _filter_mock_comparables(position, target_fee, age, limit)

        comps = []
        for raw in raw_comps:
            try:
                comp = _csv_to_comparable(raw)
                comps.append(comp)
            except Exception as e:
                print(f"[!] Failed to parse comparable: {e}")
                continue

        return comps if comps else _filter_mock_comparables(position, target_fee, age, limit)

    except Exception as e:
        print(f"[!] Local CSV comparables failed: {e}. Falling back to mock data.")
        return _filter_mock_comparables(position, target_fee, age, limit)


def _filter_mock_comparables(
    position: str,
    target_fee: float,
    age: int,
    limit: int,
) -> list[ComparableTransfer]:
    """Filter and sort mock comparables by relevance."""
    relevant = [
        c for c in MOCK_COMPARABLES
        if c.position.lower() == position.lower()
    ]

    relevant.sort(
        key=lambda c: abs(c.fee_millions - target_fee) + abs(c.age_at_transfer - age) * 0.5
    )

    return relevant[:limit]
