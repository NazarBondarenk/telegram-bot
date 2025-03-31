import requests
import os
from dotenv import load_dotenv

load_dotenv()

FACEIT_API_KEY = os.getenv("FACEIT_API_KEY")
BASE_URL = "https://open.faceit.com/data/v4"
DEBUG = False  

def get_player_profile(nickname):
    headers = {"Authorization": f"Bearer {FACEIT_API_KEY}"}
    url = f"{BASE_URL}/players"
    params = {"nickname": nickname}

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        return {
            "nickname": data.get("nickname"),
            "player_id": data.get("player_id"),
            "games": data.get("games"),
            "elo": data.get("games", {}).get("cs2", {}).get("faceit_elo", "N/A")
        }
    else:
        return None

def find_player_profile(nickname):
    possible_variants = [nickname, nickname.upper(), nickname.lower(), nickname.capitalize()]
    for variant in possible_variants:
        profile = get_player_profile(variant)
        if profile:
            return profile
    print("Player not found")
    return None

def get_player_stats(player_id, matches_count=20):
    headers = {"Authorization": f"Bearer {FACEIT_API_KEY}"}
    url = f"{BASE_URL}/players/{player_id}/history"
    params = {
        "game": "cs2",
        "limit": matches_count,
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        print(f"Failed to fetch match history: {response.status_code}")
        return None

    match_data = response.json().get("items", [])
    if not match_data:
        print("No matches found.")
        return None

    total_kills = 0
    total_headshots = 0
    total_deaths = 0
    total_rounds = 0
    total_matches = len(match_data)

    for match in match_data:
        match_id = match.get("match_id")
        stats_url = f"{BASE_URL}/matches/{match_id}/stats"
        match_response = requests.get(stats_url, headers=headers)

        if match_response.status_code != 200:
            print(f"Failed to fetch match stats for match {match_id}")
            continue

        match_stats = match_response.json()

        round_stats = match_stats.get("rounds", [{}])[0].get("round_stats", {})
        match_rounds = int(round_stats.get("Rounds", "0"))

        if DEBUG:
            print(f"Match {match_id} Rounds from match stats: {match_rounds}")

        total_rounds += match_rounds

        rounds = match_stats.get("rounds", [])
        for round_info in rounds:
            teams = round_info.get("teams", [])
            for team in teams:
                for player in team.get("players", []):
                    if player.get("player_id") == player_id:
                        player_stats = player.get("player_stats", {})

                        if DEBUG:
                            print(f"Player Stats: {player_stats}")

                        kills = int(player_stats.get("Kills", "0"))
                        headshots = int(player_stats.get("Headshots", "0"))
                        deaths = int(player_stats.get("Deaths", "0"))

                        if DEBUG:
                            print(f"Match {match_id} Stats: Kills={kills}, Headshots={headshots}, Deaths={deaths}")

                        total_kills += kills
                        total_headshots += headshots
                        total_deaths += deaths

    if total_matches == 0:
        print("No valid matches found.")
        return None

    avg_kills = total_kills / total_matches
    avg_headshots = (total_headshots / total_kills * 100) if total_kills > 0 else 0
    avg_kd = total_kills / total_deaths if total_deaths > 0 else 0
    avg_kr = total_kills / total_rounds if total_rounds > 0 else 0

    return {
        "matches_count": total_matches,
        "average_kills": round(avg_kills, 2),
        "average_headshots_percentage": round(avg_headshots, 2),
        "average_kd": round(avg_kd, 2),
        "average_kr": round(avg_kr, 2),
    }

if __name__ == "__main__":
    nickname = input("Enter the nickname of the player: ")
    profile = find_player_profile(nickname)

    if profile:
        print(f"Nickname: {profile['nickname']}")
        print(f"Player ID: {profile['player_id']}")
        print(f"ELO: {profile['elo']}")
        print("Games connected:", ", ".join(profile["games"].keys()))

        player_id = profile["player_id"]
        stats = get_player_stats(player_id)

        if stats:
            print(f"\nLast {stats['matches_count']} Matches Statistics:")
            print(f"Average Kills: {stats['average_kills']}")
            print(f"Average Headshots %: {stats['average_headshots_percentage']}")
            print(f"Average K/D: {stats['average_kd']}")
            print(f"Average K/R: {stats['average_kr']}")
    else:
        print("Player not found")
