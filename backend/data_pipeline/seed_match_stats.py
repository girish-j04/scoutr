"""
Golden Path Match Stats Seeder.

Seeds high-quality, predictable demo data for our three "Hero" players:
1001 (Firpo), 1002 (Doughty), 1003 (Henry).
This ensures the Monitoring UI shows Green, Amber, and Red alerts perfectly for the demo.
"""

import os
import sys
from datetime import datetime, timedelta

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from app.services.sqlite_service import save_match_stat

def seed_demo_stats():
    # 1. Junior Firpo (1001) - The "Target" -> Green Alert
    # 5 matches, all high rating, high tackles, high pass acc
    for i in range(5):
        date = (datetime.now() - timedelta(days=i*7)).strftime('%Y-%m-%d')
        save_match_stat(
            player_id="1001",
            match_id=f"demo_1001_{i}",
            match_date=date,
            goals=1 if i == 0 else 0,
            assists=1 if i == 2 else 0,
            tackles=4,      # High intensity
            passes_acc=88.5, # Elite passing
            rating=8.2,     # High performance
            mins=90
        )

    # 2. Alfie Doughty (1002) - The "Concern" -> Amber Alert
    # 5 matches, fluctuating ratings, medium stats
    for i in range(5):
        date = (datetime.now() - timedelta(days=i*7)).strftime('%Y-%m-%d')
        save_match_stat(
            player_id="1002",
            match_id=f"demo_1002_{i}",
            match_date=date,
            goals=0,
            assists=0,
            tackles=2,      # Average intensity
            passes_acc=72.0, # Average passing
            rating=6.8,     # Average performance
            mins=90
        )

    # 3. Rico Henry (1003) - The "Risk" -> Red Alert
    # 5 matches, low ratings or low involvement
    for i in range(5):
        date = (datetime.now() - timedelta(days=i*7)).strftime('%Y-%m-%d')
        save_match_stat(
            player_id="1003",
            match_id=f"demo_1003_{i}",
            match_date=date,
            goals=0,
            assists=0,
            tackles=1,      # Low intensity
            passes_acc=65.0, # Poor passing
            rating=5.4,     # Poor performance
            mins=45 if i < 2 else 90 # Simulated coming off early
        )

    print("✅ Seeded Golden Path demo match stats (Firpo, Doughty, Henry).")

if __name__ == "__main__":
    seed_demo_stats()
