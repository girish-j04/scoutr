import json
import os

CACHE_DIR = os.path.join(os.path.dirname(__file__), 'data/db')

def seed_golden_path():
    """
    Seeds the API fallback for the core demo query:
    'Find me a left-back under 24, comfortable in a high press, contract expiring within 12 months,
    available for under €7M, preferably from a league with similar intensity to the Championship.'
    """
    golden_path_response = {
        "status": "success",
        "cached_for_demo": True,
        "candidates": [
            {
                "player_id": 999999,
                "name": "Leif Davis",
                "club": "Leeds United",
                "league": "Championship",
                "age": 23,
                "position": "left-back",
                "pressure_success_rate": 81.5,
                "contract_expiry": "2024-06-30",
                "market_value": 6.5,
                "progressive_carries": 94,
                "xA": 6.2,
                "xG": 1.4
            },
            {
                "player_id": 28573,
                "name": "Felix Agu",
                "club": "Werder Bremen",
                "league": "1. Bundesliga",
                "age": 23,
                "position": "left-back",
                "pressure_success_rate": 78.1,
                "contract_expiry": "2024-06-30",
                "market_value": 6.8,
                "progressive_carries": 62,
                "xA": 3.1,
                "xG": 0.8
            },
            {
                "player_id": 10336,
                "name": "Álex Grimaldo",
                "club": "Bayer Leverkusen",
                "league": "1. Bundesliga",
                "age": 23,
                "position": "left-back",
                "pressure_success_rate": 75.0,
                "contract_expiry": "2024-06-30",
                "market_value": 6.9,
                "progressive_carries": 88,
                "xA": 4.5,
                "xG": 1.1
            }
        ]
    }
    
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_file = os.path.join(CACHE_DIR, 'golden_path.json')
    
    with open(cache_file, 'w') as f:
        json.dump(golden_path_response, f, indent=4)
        
    print(f"✅ Golden path safely seeded at {cache_file}")

if __name__ == "__main__":
    seed_golden_path()
