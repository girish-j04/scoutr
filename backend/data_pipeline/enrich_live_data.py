"""
Standalone Live Data Enrichment Script.

Run this ONCE to fetch current season stats for your players from API-Football
and store them in your local SQLite database.

Usage:
    export RAPID_API_KEY="your_key"
    python3 data_pipeline/enrich_live_data.py [limit]
"""

import os
import sys
import time
import json
import requests
import sqlite3

# Add backend to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

# ── SAFETY SCRUB ─────────────────────────────────────────────────────────────
# We MUST remove non-Chroma variables from the environment before importing 
# chroma_service, or ChromaDB's internal Settings will crash the process.
RAPID_API_KEY_VAL = os.environ.get("RAPID_API_KEY")
for key in list(os.environ.keys()):
    if key.startswith("SCOUTR_") or key == "RAPID_API_KEY":
        os.environ.pop(key)

from app.services.sqlite_service import save_api_football_id, save_form_cache, DB_PATH
from app.services.chroma_service import chroma_service

API_BASE = "https://api-football-v1.p.rapidapi.com/v3"
SEASON = 2024

def get_headers(api_key):
    return {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com",
    }

def compute_form_score(stats):
    """Simplified form calculator for the offline script."""
    games = stats.get("games", {})
    appearences = games.get("appearences") or 0
    if appearences == 0: return 0.0, "low"
    
    rating = float(games.get("rating") or 6.5)
    accuracy = float((stats.get("passes", {}) or {}).get("accuracy") or 70.0)
    tackles = (stats.get("tackles", {}) or {}).get("total") or 0
    tpg = tackles / appearences
    
    score = ((rating - 5.0) * 15) + (accuracy - 50) * 0.6
    score = max(0, min(100, round(score, 1)))
    
    fit = "high" if tpg > 2.0 and accuracy > 80 else "medium"
    return score, fit

def enrich_live_data(api_key, limit=50):
    print(f"Connecting to ChromaDB...")
    results = chroma_service.collection.get()
    player_ids = results.get("ids", [])
    metadatas = results.get("metadatas", [])
    
    print(f"Found {len(player_ids)} players. Enriched limit set to: {limit}")
    count = 0
    
    headers = get_headers(api_key)
    
    for i in range(min(len(player_ids), limit)):
        pid = player_ids[i]
        name = metadatas[i].get("name")
        
        print(f"[{i+1}/{limit}] Processing {name}...")
        
        try:
            # 1. Resolve ID
            search = requests.get(f"{API_BASE}/players", headers=headers, params={"search": name, "season": SEASON}, timeout=10)
            res = search.json().get("response", [])
            if not res: 
                print(f"  - Player not found on API")
                continue
                
            api_id = res[0]["player"]["id"]
            save_api_football_id(pid, api_id, name)
            
            # 2. Get Stats
            stats_resp = requests.get(f"{API_BASE}/players", headers=headers, params={"id": api_id, "season": SEASON}, timeout=10)
            stats_data = stats_resp.json().get("response", [])
            if not stats_data: continue
            
            stats = stats_data[0].get("statistics", [{}])[0]
            form_score, style_fit = compute_form_score(stats)
            app = stats.get("games", {}).get("appearences") or 0
            
            save_form_cache(pid, json.dumps(stats), form_score, style_fit, int(app))
            print(f"  ✅ Saved: Score {form_score}, Fit {style_fit}")
            
            count += 1
            time.sleep(1.5) # Be gentle with API
            
        except Exception as e:
            print(f"  ❌ Error: {e}")

    print(f"\nDone! Enriched {count} players with live form data.")

if __name__ == "__main__":
    key = RAPID_API_KEY_VAL
    if not key:
        print("Error: Please set RAPID_API_KEY environment variable first (e.g. export RAPID_API_KEY='...')")
        sys.exit(1)
        
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    enrich_live_data(key, limit)
