# Dev 3 Integration Contracts

For Dev 1, Dev 2, and Dev 4. Publish early.

## 1. Tactical Fit Output Schema

Returned by `scoutr.agents.tactical_fit.evaluate_tactical_fit(player_id)`.

```json
{
  "tactical_fit_score": 0-100,
  "fit_explanation": "plain English text",
  "heatmap_zones": ["zone1", "zone2"],
  "formation_compatibility": ["4-3-3", "4-2-3-1"]
}
```

## 2. Monitoring Alerts Schema

Returned by `scoutr.agents.monitoring.check_watchlist(watchlist)`.

```json
{
  "alerts": [
    {
      "player_id": 1,
      "type": "contract_urgency | competitor_scout | club_finances",
      "severity": "green | amber | red",
      "message": "text",
      "timestamp": "ISO8601"
    }
  ]
}
```

## 3. POST /export

**Request:**
```
POST /export
Content-Type: application/json

{
  "player_ids": [1, 2, 3],
  "query": "optional context",
  "club": "Leeds United"
}
```

**Response:** PDF binary, `Content-Type: application/pdf`

**Fallback:** If `/player/{id}` or other APIs fail, uses golden path dataset.

**Dev 1 wiring:**
```python
from scoutr.api.export_router import export_router
app.include_router(export_router)
```

## 4. Player Schema (Dev 1) — Tactical Fit Inputs

Dev 3 expects `/player/{id}` to return (per ScoutR.md):

- `player_id`, `name`, `club`, `league`, `age`, `position`, `contract_expiry`, `market_value`
- `press_metrics`: `{ppda`, `pressure_success_rate}`
- `defensive_actions_per_90`
- `progressive_carries`, `xA`, `xG`
- `heatmap_centroid` (optional): `{x, y}` normalized 0-1 for positional heatmap centroid

## 5. Golden Path Player IDs

Use these IDs for the demo:
- `1001` — Junior Firpo (Real Betis)
- `1002` — Alfie Doughty (Luton Town)
- `1003` — Rico Henry (Brentford)
