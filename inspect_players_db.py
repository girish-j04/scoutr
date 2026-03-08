import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'backend/data_pipeline/data/db/players.db')

def inspect_db():
    if not os.path.exists(DB_PATH):
        print(f"DB not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("--- Player Match Stats ---")
    cursor.execute("SELECT DISTINCT player_id FROM player_match_stats LIMIT 10")
    pids = cursor.fetchall()
    print(f"Sample PIDs in match stats: {pids}")
    
    if pids:
        pid = pids[0][0]
        cursor.execute("SELECT * FROM player_match_stats WHERE player_id = ?", (pid,))
        matches = cursor.fetchall()
        print(f"Matches for {pid}: {len(matches)}")
        print(f"Sample match: {matches[0] if matches else 'N/A'}")
    else:
        print("No match stats found.")

    conn.close()

if __name__ == "__main__":
    inspect_db()
