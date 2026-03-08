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
from app.services.sqlite_service import get_recent_matches


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

def _form_update_alerts(
    player_id: int,
    player: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Generate form_update alerts using historical StatsBomb match data from local SQLite.
    Calculates form based on the most recent 5 matches.
    """
    matches = get_recent_matches(str(player_id), limit=5)
    if not matches:
        return []

    # Calculate average rating and metrics over last matches
    avg_rating = sum(m["rating"] for m in matches) / len(matches)
    total_goals = sum(m["goals"] for m in matches)
    total_assists = sum(m["assists"] for m in matches)
    total_tackles = sum(m["tackles"] for m in matches)
    avg_pass_acc = sum(m["passes_accuracy"] for m in matches) / len(matches)

    # Simplified local Form Score (0-100)
    # Goal/Assist in last matches is a big boost.
    form_score = (avg_rating - 5.0) * 15 + (total_goals + total_assists) * 5 + (avg_pass_acc - 70) * 0.5
    form_score = max(0, min(100, round(form_score, 1)))

    # Style fit based on tackles (defensive intensity) or passing
    style_fit = "low"
    if total_tackles > 5 and avg_pass_acc > 75:
        style_fit = "high"
    elif total_tackles > 2 or avg_pass_acc > 70:
        style_fit = "medium"

    alerts = []
    ts = datetime.now(timezone.utc).isoformat()
    name = player.get("name", "Player")

    if form_score >= 70:
        severity = "green"
        msg = f"{name} — Strong form (Score: {form_score}/100) over last {len(matches)} matches. Trending up."
    elif form_score >= 45:
        severity = "amber"
        msg = f"{name} — Stable form (Score: {form_score}/100). Recent match rating: {matches[0]['rating']}."
    else:
        severity = "red"
        msg = f"{name} — Poor form (Score: {form_score}/100). Stats highlight lack of involvement."

    alerts.append({
        "player_id": player_id,
        "type": "form_update",
        "severity": severity,
        "message": msg,
        "timestamp": ts,
        "form_score": form_score,
        "style_fit": style_fit,
        "recent_matches": matches[:3] # Include snippets of last 3 games
    })

    return alerts



def check_watchlist(
    watchlist: list[int],
    api_base_url: str = "http://localhost:8000",
    include_mock_alerts: bool = True,
    include_form_alerts: bool = True,
) -> dict[str, list[dict[str, Any]]]:
    """Check watchlist and return alerts. Output schema for Dev 4.

    Returns:
        {"alerts": [{"player_id", "type", "severity", "message", "timestamp"}, ...]}
    """
    alerts: list[dict[str, Any]] = []
    players: list[dict[str, Any]] = []

    for pid in watchlist:
        player = _get_player(pid, api_base_url)
        
        # If we have a profile, add specific metadata alerts
        if player:
            players.append(player)
            alerts.extend(_contract_urgency_alerts(pid, player))
            if include_form_alerts:
                alerts.extend(_form_update_alerts(pid, player))
        else:
            # EVEN IF NO PROFILE, check for match history alerts
            if include_form_alerts:
                # Create a minimal dummy player object so _form_update_alerts works
                dummy_player = {"name": f"Player {pid}"}
                alerts.extend(_form_update_alerts(pid, dummy_player))

    if include_mock_alerts:
        alerts.extend(_mock_competitor_scout_alerts(watchlist))
        alerts.extend(_mock_club_finances_alerts(watchlist, players))

    # Sort by severity (red first, then amber, then green)
    severity_order = {"red": 0, "amber": 1, "green": 2}
    alerts.sort(key=lambda a: (severity_order.get(a["severity"], 3), a["timestamp"]))

    return {"alerts": alerts}
