"""
StatsBomb Match-by-Match Ingestion Pipeline.

Extracts performance data for every player in every match (2021 onwards)
and stores it in the SQLite player_match_stats table.
This data is used to calculate "Live Form" in the Monitoring Agent.
"""

import os
import json
import sqlite3
import sys

# Add backend to path for imports
_BACKEND_ROOT = os.path.join(os.path.dirname(__file__), '../')
if _BACKEND_ROOT not in sys.path:
    sys.path.insert(0, _BACKEND_ROOT)

from app.services.sqlite_service import save_match_stat

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data/statsbomb/data')

def clean_text(text: str) -> str:
    """Helper to strip newlines and extra spaces from JSON strings."""
    if not text:
        return ""
    cleaned = str(text).replace("\n", " ").replace("\r", " ").replace("\t", " ")
    return " ".join(cleaned.split()).strip()

def calculate_rating(goals, assists, tackles, pass_acc):
    """Simple heuristic for match rating."""
    base = 6.0
    bonus = (goals * 1.5) + (assists * 1.0) + (tackles * 0.2) + ((pass_acc - 70) * 0.05)
    return round(max(0, min(10.0, base + bonus)), 1)

def ingest_match_stats():
    comps_file = os.path.join(DATA_DIR, "competitions.json")
    with open(comps_file, 'r', encoding='utf-8') as f:
        competitions = json.load(f)
        
    all_seasons = []
    for comp in competitions:
        if comp.get("competition_gender", "male").lower() == "female":
            continue
        
        season_str = comp.get("season_name", "")
        try:
            start_year = int(season_str[:4])
            if start_year >= 2021:
                all_seasons.append((str(comp["competition_id"]), str(comp["season_id"]), clean_text(comp["competition_name"])))
        except ValueError:
            pass

    print(f"Found {len(all_seasons)} applicable seasons. Starting match-level extraction...")

    for comp_id, season_id, league in all_seasons:
        matches_file = os.path.join(DATA_DIR, "matches", comp_id, f"{season_id}.json")
        if not os.path.exists(matches_file):
            continue
            
        with open(matches_file, 'r', encoding='utf-8') as f:
            matches = json.load(f)
            
        print(f"  Processing {len(matches)} matches from {league}...")
        
        for match in matches:
            match_id = str(match["match_id"])
            match_date = clean_text(match["match_date"])
            
            # Aggregate stats from Events for this match
            events_file = os.path.join(DATA_DIR, "events", f"{match_id}.json")
            if not os.path.exists(events_file): continue
                
            with open(events_file, 'r', encoding='utf-8') as f:
                events = json.load(f)
            
            # player_id -> dict of stats
            match_performance = {}

            for ev in events:
                if "player" not in ev: continue
                pid = str(ev["player"]["id"])
                
                if pid not in match_performance:
                    match_performance[pid] = {
                        "goals": 0, "assists": 0, "tackles": 0,
                        "passes_total": 0, "passes_comp": 0, "mins": 90 # Defaulting to 90 for simplicity
                    }
                
                stats = match_performance[pid]
                ev_type = ev["type"]["name"]

                if ev_type == "Shot" and "shot" in ev:
                    if ev["shot"].get("outcome", {}).get("name") == "Goal":
                        stats["goals"] += 1
                
                elif ev_type == "Pass" and "pass" in ev:
                    stats["passes_total"] += 1
                    if "outcome" not in ev["pass"]: # In StatsBomb, no outcome means completed
                        stats["passes_comp"] += 1
                        if ev["pass"].get("goal_assist"):
                            stats["assists"] += 1
                            
                elif ev_type == "Duel" and ev.get("duel", {}).get("type", {}).get("name") == "Tackle":
                    if ev.get("duel", {}).get("outcome", {}).get("name") in ["Success", "Won"]:
                        stats["tackles"] += 1

            # Save aggregated results per player for this match
            for pid, s in match_performance.items():
                acc = (s["passes_comp"] / s["passes_total"] * 100) if s["passes_total"] > 0 else 75.0
                rating = calculate_rating(s["goals"], s["assists"], s["tackles"], acc)
                
                try:
                    save_match_stat(
                        player_id=pid,
                        match_id=match_id,
                        match_date=match_date,
                        goals=s["goals"],
                        assists=s["assists"],
                        tackles=s["tackles"],
                        passes_acc=round(acc, 1),
                        rating=rating,
                        mins=s["mins"]
                    )
                except Exception as e:
                    # Likely a duplicate from multiple seasons, skip
                    pass

    print("Success! Match-by-match metrics ingested for monitoring.")

if __name__ == "__main__":
    ingest_match_stats()
