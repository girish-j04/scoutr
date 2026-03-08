"""PDF export service for scouting reports.

Uses pdfkit (requires wkhtmltopdf). Generates a scouting report with cover,
player dossiers (name, club, age, tactical score, contract risk, fee range, key stats).
"""

from datetime import datetime, timezone
from typing import Any

from scoutr.agents.monitoring import _months_until_expiry
from scoutr.agents.tactical_fit import evaluate_tactical_fit
from scoutr.golden_path import get_golden_path_player, get_golden_path_player_ids
from scoutr.scoring.tactical_score import compute_tactical_fit_score

try:
    import pdfkit
    PDFKIT_AVAILABLE = True
except (ImportError, OSError):
    PDFKIT_AVAILABLE = False

try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False


def _get_player(player_id: int, api_base_url: str) -> dict[str, Any] | None:
    """Fetch player from API or golden path."""
    import httpx
    url = f"{api_base_url.rstrip('/')}/player/{player_id}"
    try:
        with httpx.Client(timeout=10.0) as client:
            r = client.get(url)
            if r.status_code == 200:
                return r.json()
    except Exception:
        pass
    return get_golden_path_player(player_id)


def _get_fee_range(player_id: int, api_base_url: str) -> tuple[str, str, str]:
    """Fetch fee range from /comparables or use market_value as fallback."""
    import httpx
    url = f"{api_base_url.rstrip('/')}/comparables"
    try:
        with httpx.Client(timeout=10.0) as client:
            r = client.get(url, params={"player_id": player_id})
            if r.status_code == 200:
                data = r.json()
                low = data.get("low_fee", data.get("low")) or "N/A"
                mid = data.get("mid_fee", data.get("mid")) or "N/A"
                high = data.get("high_fee", data.get("high")) or "N/A"
                return (str(low), str(mid), str(high))
    except Exception:
        pass
    player = get_golden_path_player(player_id)
    if player and "market_value" in player:
        mv = player["market_value"]
        return (f"€{int(mv * 0.7):,}", f"€{int(mv):,}", f"€{int(mv * 1.3):,}")
    return ("N/A", "N/A", "N/A")


def _contract_risk(contract_expiry: str | None) -> str:
    """Return contract risk: green, amber, or red."""
    months = _months_until_expiry(contract_expiry)
    if months is None:
        return "N/A"
    if months < 3:
        return "red"
    if months < 6:
        return "amber"
    return "green"


def _build_html(
    query: str,
    club: str,
    players: list[dict],
    tactical_fits: dict[int, dict],
    fee_ranges: dict[int, tuple[str, str, str]],
) -> str:
    """Build HTML for PDF report."""
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    rows = []
    for p in players:
        pid = p.get("player_id", 0)
        tf = tactical_fits.get(pid, {})
        low, mid, high = fee_ranges.get(pid, ("N/A", "N/A", "N/A"))
        risk = _contract_risk(p.get("contract_expiry"))
        score = tf.get("tactical_fit_score", compute_tactical_fit_score(p))
        press = p.get("press_metrics", {})
        ppda = press.get("ppda", "N/A")
        prog = p.get("progressive_carries", "N/A")
        rows.append(f"""
        <tr>
            <td>{p.get('name', 'N/A')}</td>
            <td>{p.get('club', 'N/A')}</td>
            <td>{p.get('age', 'N/A')}</td>
            <td>{score}</td>
            <td>{risk}</td>
            <td>{low} - {high}</td>
            <td>PPDA: {ppda}, Prog: {prog}</td>
        </tr>""")

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>ScoutR Scouting Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; color: #333; }}
        h1 {{ color: #1a1a1a; border-bottom: 2px solid #0066cc; padding-bottom: 8px; }}
        .meta {{ color: #666; margin-bottom: 24px; font-size: 14px; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
        th {{ background: #0066cc; color: white; }}
        tr:nth-child(even) {{ background: #f9f9f9; }}
        .cover {{ margin-bottom: 40px; }}
    </style>
</head>
<body>
    <div class="cover">
        <h1>ScoutR Scouting Report</h1>
        <p class="meta"><strong>Club:</strong> {club} | <strong>Date:</strong> {date_str}</p>
        <p class="meta"><strong>Query:</strong> {query or 'N/A'}</p>
    </div>
    <h2>Player Dossiers</h2>
    <table>
        <thead>
            <tr>
                <th>Name</th>
                <th>Club</th>
                <th>Age</th>
                <th>Tactical Score</th>
                <th>Contract Risk</th>
                <th>Fee Range</th>
                <th>Key Stats</th>
            </tr>
        </thead>
        <tbody>
            {''.join(rows)}
        </tbody>
    </table>
</body>
</html>"""
    return html


def generate_pdf(
    player_ids: list[int],
    query: str = "",
    club: str = "Leeds United",
    api_base_url: str = "http://localhost:8000",
) -> bytes:
    """Generate PDF scouting report. Falls back to golden path if API fails.

    Args:
        player_ids: List of player IDs to include
        query: Original search query (for cover)
        club: Buying club name
        api_base_url: Base URL for Dev 1 API

    Returns:
        PDF as bytes
    """
    if not player_ids:
        player_ids = get_golden_path_player_ids()

    players: list[dict[str, Any]] = []
    tactical_fits: dict[int, dict] = {}
    fee_ranges: dict[int, tuple[str, str, str]] = {}

    for pid in player_ids:
        player = _get_player(pid, api_base_url)
        if not player:
            continue
        players.append(player)
        tactical_fits[pid] = evaluate_tactical_fit(pid, api_base_url, use_claude=False)
        fee_ranges[pid] = _get_fee_range(pid, api_base_url)

    if not players:
        players = [get_golden_path_player(pid) for pid in get_golden_path_player_ids()]
        players = [p for p in players if p]
        for p in players:
            pid = p["player_id"]
            tactical_fits[pid] = evaluate_tactical_fit(pid, api_base_url, use_claude=False)
            fee_ranges[pid] = _get_fee_range(pid, api_base_url)

    html = _build_html(query, club, players, tactical_fits, fee_ranges)

    if PDFKIT_AVAILABLE:
        try:
            return pdfkit.from_string(html)
        except (OSError, IOError):
            pass
    if WEASYPRINT_AVAILABLE:
        return HTML(string=html).write_pdf()
    raise RuntimeError(
        "PDF generation requires either: (1) pdfkit + wkhtmltopdf, or (2) weasyprint. "
        "Install: pip install weasyprint OR sudo apt-get install wkhtmltopdf"
    )
