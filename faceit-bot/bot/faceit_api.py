import requests
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv


load_dotenv()

FACEIT_API_KEY = os.getenv("FACEIT_API_KEY")
BASE_URL = "https://open.faceit.com/data/v4"

def get_players_matches(player_id, hours=24):
    headers = {
    "Authorization": f"Bearer {FACEIT_API_KEY}"
    }
    
    now = datetime.now(timezone.utc)
    time_limit = now - timedelta(hours=hours)
    
    endpoint = f"{BASE_URL}/players/{player_id}/history"
    
    params = {
        "game": "cs2",
        "from": int(time_limit.timestamp()),
        "to": int(now.timestamp()),
        "limit": 50
    }
    
    response = requests.get(endpoint, headers=headers, params=params)
    
    if response.status_code == 200:
        matches = response.json().get("items", [])
        return len(matches)
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return 0
    
if __name__ == "__main__":
    player_id = "bda473f0-7d84-423d-b96b-162f24db9c79"
    hours = 27
    match_count = get_players_matches(player_id, hours)
    print(f"For last {hours} hours was played {match_count} matches")
    