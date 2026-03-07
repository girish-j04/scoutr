"""Quick verification script for ScoutR unified backend."""

import httpx
import json
import sys


BASE_URL = "http://localhost:8000"
GOLDEN_QUERY = (
    "Find me a left-back under 24, comfortable in a high press, "
    "contract expiring within 12 months, available for under 7M, "
    "preferably from a league with similar intensity to the Championship."
)


def test_health():
    r = httpx.get(f"{BASE_URL}/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    print("[PASS] Health check")


def test_root():
    r = httpx.get(f"{BASE_URL}/")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    print("[PASS] Root endpoint")


# ── Dev 1 Data Layer Endpoints ──

def test_search():
    """Test the POST /search data layer endpoint."""
    payload = {
        "position": "left-back",
        "max_age": 24,
        "min_press_score": 30.0,
    }
    r = httpx.post(f"{BASE_URL}/search", json=payload, timeout=15)
    assert r.status_code == 200
    data = r.json()
    assert "candidates" in data, "Response missing 'candidates' key"
    print(f"[PASS] POST /search - found {len(data['candidates'])} candidates")
    if data["candidates"]:
        c = data["candidates"][0]
        print(f"  Sample: {c.get('name', 'N/A')} ({c.get('club', 'N/A')})")


def test_comparables():
    """Test the GET /comparables data layer endpoint."""
    r = httpx.get(f"{BASE_URL}/comparables?target_fee=15.0", timeout=10)
    assert r.status_code == 200
    data = r.json()
    assert "comparables" in data, "Response missing 'comparables' key"
    print(f"[PASS] GET /comparables - found {len(data['comparables'])} comparable transfers")


# ── Dev 2 AI Agent Endpoints ──

def test_golden_path():
    """Test POST /query with golden path demo query."""
    r = httpx.post(f"{BASE_URL}/query", json={"query": GOLDEN_QUERY}, timeout=30)
    assert r.status_code == 200
    data = r.json()

    assert len(data["dossiers"]) == 3, f"Expected 3 dossiers, got {len(data['dossiers'])}"
    assert data["parsed_criteria"]["position"] == "Left-Back"
    assert data["parsed_criteria"]["max_age"] == 24

    for d in data["dossiers"]:
        p = d["player"]
        assert p["name"], "Player name missing"
        assert p["club"], "Club missing"
        assert d["fee_range"]["low_estimate"] > 0, "Fee range missing"
        assert d["contract_risk"] in ("green", "amber", "red"), "Invalid contract risk"
        assert d["ranking_reason"], "Ranking reason missing"
        assert d["scouting_summary"], "Scouting summary missing"
        assert d["valuation_narrative"], "Valuation narrative missing"
        assert d["negotiation_insight"], "Negotiation insight missing"
        print(f"  #{d['rank']} {p['name']} ({p['club']}) - "
              f"Fee: {d['fee_range']['low_estimate']}-{d['fee_range']['high_estimate']}M - "
              f"Risk: {d['contract_risk']}")

    print("[PASS] Golden path query - 3 complete dossiers")


def test_sse_stream():
    """Test POST /query/stream SSE streaming endpoint."""
    with httpx.stream(
        "POST", f"{BASE_URL}/query/stream",
        json={"query": GOLDEN_QUERY},
        timeout=30,
    ) as r:
        events = []
        for line in r.iter_lines():
            if line.startswith("data:"):
                data_str = line[len("data:"):].strip()
                if data_str:
                    events.append(json.loads(data_str))
            elif line.startswith("event:"):
                pass

        steps = [e.get("step", "") for e in events if "step" in e]
        assert "received_query" in steps, "Missing received_query event"
        assert "parsing_query" in steps, "Missing parsing_query event"
        assert "searching_players" in steps, "Missing searching_players event"
        assert "starting_valuation" in steps, "Missing starting_valuation event"
        assert "assembly_complete" in steps, "Missing assembly_complete event"

        final_events = [e for e in events if "dossiers" in e]
        assert len(final_events) >= 1, "Missing final result event"

        print(f"[PASS] SSE stream - {len(events)} events received")
        for s in steps:
            print(f"  -> {s}")


if __name__ == "__main__":
    print("=== ScoutR Unified Backend Verification ===\n")
    try:
        test_health()
        test_root()
        print("\n--- Data Layer Endpoints ---")
        test_search()
        test_comparables()
        print("\n--- AI Agent Endpoints ---")
        test_golden_path()
        test_sse_stream()
        print("\n=== ALL TESTS PASSED ===")
    except Exception as e:
        print(f"\n[FAIL] {e}")
        sys.exit(1)
