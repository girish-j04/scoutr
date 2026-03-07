import requests

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    print("✅ Health check passed: ", response.json())

def test_search():
    print("\nTesting /search endpoint...")
    payload = {
        "position": "left-back",
        "max_age": 24,
        "min_press_score": 75.0
    }
    response = requests.post(f"{BASE_URL}/search", json=payload)
    if response.status_code != 200:
        print(f"❌ Error {response.status_code}: {response.text}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert "candidates" in data, "Response JSON missing 'candidates' key"
    print("✅ Search passed.")
    print(f"Found {len(data['candidates'])} candidates.")
    
def test_player_profile():
    print("\nTesting /player/{id} endpoint...")
    player_id = "999999" # Leif Davis mock
    response = requests.get(f"{BASE_URL}/player/{player_id}")
    if response.status_code != 200:
        print(f"❌ Error {response.status_code}: {response.text}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert "contract_expiry" in data, "Response JSON missing 'contract_expiry' key"
    assert "market_value" in data, "Response JSON missing 'market_value' key"
    print("✅ Player Profile passed: ", data)
    
def test_comparables():
    print("\nTesting /comparables endpoint...")
    response = requests.get(f"{BASE_URL}/comparables?target_fee=15.0")
    if response.status_code != 200:
        print(f"❌ Error {response.status_code}: {response.text}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert "comparables" in data, "Response JSON missing 'comparables' key"
    assert len(data["comparables"]) == 5, f"Expected 5 comparables, got {len(data['comparables'])}"
    print("✅ Comparables passed: found 5 close transfers.")
    
    import json
    print("Top 5 Comparables for €15.0M:")
    print(json.dumps(data["comparables"], indent=2))

if __name__ == "__main__":
    print(f"Running API tests against {BASE_URL}...\n")
    try:
        test_health()
        test_search()
        test_player_profile()
        test_comparables()
        print("\nAll endpoints returned the expected shape. Tests passed!")
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Connection Error: Ensure your FastAPI server is running at {BASE_URL}")
