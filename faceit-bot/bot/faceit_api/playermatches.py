import requests
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv

load_dotenv()

FACEIT_API_KEY = os.getenv("FACEIT_API_KEY")
BASE_URL = "https://open.faceit.com/data/v4"

def get_players_matches(player_id, hours=80):
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
        "limit": 10000
    }
    
    response = requests.get(endpoint, headers=headers, params=params)
    
    if response.status_code == 200:
        matches = response.json().get("items", [])
        return len(matches)
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return 0

