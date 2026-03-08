"""Monitoring Agent.

Watches a target watchlist and emits alerts for:
- Contract urgency (contract_expiry < 6 months)
- Competitor scout (mock for hackathon)
- Club finances (mock for hackathon)
"""

from datetime import datetime, timezone
from typing import Any, Literal

import httpx

from scoutr.golden_path import get_golden_path_player, get_golden_path_players


AlertType = Literal["contract_urgency", "competitor_scout", "club_finances"]
Severity = Literal["green", "amber", "red"]


def _get_player(
    player_id: int,
    api_base_url: str = "http://localhost:8000",
) -> dict[str, Any] | None:
    """Fetch player from API or golden path."""
    url = f"{api_base_url.rstrip('/')}/player/{player_id}"
    try:
        with httpx.Client(timeout=10.0) as client:
            r = client.get(url)
            if r.status_code == 200:
                return r.json()
    except Exception:
        pass
    return get_golden_path_player(player_id)


def _months_until_expiry(contract_expiry: str | None) -> float | None:
    """Return months until contract expiry, or None if invalid."""
    if not contract_expiry:
        return None
    try:
        end = datetime.fromisoformat(contract_expiry.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        if end.tzinfo is None:
            end = end.replace(tzinfo=timezone.utc)
        delta = end - now
        return delta.days / 30.0
    except Exception:
        return None


def _contract_urgency_alerts(
    player_id: int,
    player: dict[str, Any],
) -> list[dict[str, Any]]:
    """Generate contract_urgency alerts based on contract_expiry."""
    alerts = []
    expiry = player.get("contract_expiry")
    months = _months_until_expiry(expiry)

    if months is None:
        return alerts

    name = player.get("name", "Unknown")
    ts = datetime.now(timezone.utc).isoformat()

    if months < 0:
        alerts.append({
            "player_id": player_id,
            "type": "contract_urgency",
            "severity": "red",
            "message": f"{name} — contract has expired. Free agent.",
            "timestamp": ts,
        })
    elif months < 3:
        alerts.append({
            "player_id": player_id,
            "type": "contract_urgency",
            "severity": "red",
            "message": f"{name} — contract expires in {int(months * 30)} days. Urgent.",
            "timestamp": ts,
        })
    elif months < 6:
        alerts.append({
            "player_id": player_id,
            "type": "contract_urgency",
            "severity": "amber",
            "message": f"{name} — contract expires in {int(months)} months. Act soon.",
            "timestamp": ts,
        })
    elif months < 12:
        alerts.append({
            "player_id": player_id,
            "type": "contract_urgency",
            "severity": "green",
            "message": f"{name} — contract expires in {int(months)} months. Monitor.",
            "timestamp": ts,
        })

    return alerts


def _mock_competitor_scout_alerts(
    player_ids: list[int],
) -> list[dict[str, Any]]:
    """[DEMO] Mock competitor scout alerts. Stub for hackathon."""
    alerts = []
    ts = datetime.now(timezone.utc).isoformat()
    # Only alert for first player as demo
    if player_ids:
        alerts.append({
            "player_id": player_ids[0],
            "type": "competitor_scout",
            "severity": "amber",
            "message": "[DEMO] Rival club scouts spotted at recent match. Interest may be growing.",
            "timestamp": ts,
        })
    return alerts


def _mock_club_finances_alerts(
    player_ids: list[int],
    players: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """[DEMO] Mock club finances alerts. Stub for hackathon."""
    alerts = []
    ts = datetime.now(timezone.utc).isoformat()
    # Pick one lower-value club as "under pressure" for demo
    for p in players:
        pid = p.get("player_id")
        if pid in player_ids and p.get("market_value", 0) < 4_000_000:
            alerts.append({
                "player_id": pid,
                "type": "club_finances",
                "severity": "amber",
                "message": f"[DEMO] {p.get('club', 'Club')} may be open to offers due to financial position.",
                "timestamp": ts,
            })
            break
    return alerts


def check_watchlist(
    watchlist: list[int],
    api_base_url: str = "http://localhost:8000",
    include_mock_alerts: bool = True,
) -> dict[str, list[dict[str, Any]]]:
    """Check watchlist and return alerts. Output schema for Dev 4.

    Returns:
        {"alerts": [{"player_id", "type", "severity", "message", "timestamp"}, ...]}
    """
    alerts: list[dict[str, Any]] = []
    players: list[dict[str, Any]] = []

    for pid in watchlist:
        player = _get_player(pid, api_base_url)
        if player:
            players.append(player)
            alerts.extend(_contract_urgency_alerts(pid, player))

    if include_mock_alerts:
        alerts.extend(_mock_competitor_scout_alerts(watchlist))
        alerts.extend(_mock_club_finances_alerts(watchlist, players))

    # Sort by severity (red first, then amber, then green)
    severity_order = {"red": 0, "amber": 1, "green": 2}
    alerts.sort(key=lambda a: (severity_order.get(a["severity"], 3), a["timestamp"]))

    return {"alerts": alerts}
