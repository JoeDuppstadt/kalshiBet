import requests
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import os

# ────────────────────────────────────────────────
#  CONFIGURATION
# ────────────────────────────────────────────────

load_dotenv()  # loads .env into environment variables

API_KEY = os.getenv("ODDS_API_KEY")

REGIONS = "us"  # usually "us" for FanDuel
MARKETS = "h2h,spreads,totals"  # moneyline, spread, total
ODDS_FORMAT = "american"  # "american" or "decimal"
DATE_FORMAT = "iso"

# Only FanDuel
BOOKMAKERS = "fanduel"

# How many days ahead to look (API usually returns ~7–14 days worth)
DAYS_AHEAD = 0

TEAM_ABBRS = {
    "Atlanta Hawks": "ATL",
    "Boston Celtics": "BOS",
    "Brooklyn Nets": "BKN",
    "Charlotte Hornets": "CHA",
    "Chicago Bulls": "CHI",
    "Cleveland Cavaliers": "CLE",
    "Dallas Mavericks": "DAL",
    "Denver Nuggets": "DEN",
    "Detroit Pistons": "DET",
    "Golden State Warriors": "GSW",
    "Houston Rockets": "HOU",
    "Indiana Pacers": "IND",
    "LA Clippers": "LAC",
    "Los Angeles Lakers": "LAL",
    "Memphis Grizzlies": "MEM",
    "Miami Heat": "MIA",
    "Milwaukee Bucks": "MIL",
    "Minnesota Timberwolves": "MIN",
    "New Orleans Pelicans": "NOP",
    "New York Knicks": "NYK",
    "Oklahoma City Thunder": "OKC",
    "Orlando Magic": "ORL",
    "Philadelphia 76ers": "PHI",
    "Phoenix Suns": "PHX",
    "Portland Trail Blazers": "POR",
    "Sacramento Kings": "SAC",
    "San Antonio Spurs": "SAS",
    "Toronto Raptors": "TOR",
    "Utah Jazz": "UTA",
    "Washington Wizards": "WAS",
    # Add any variants like "LA Clippers" vs "Los Angeles Clippers" if needed
}

# ────────────────────────────────────────────────

def get_nba_odds():
    sport_key = "basketball_nba"
    formatted_odds_list = []


    curr_utc = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    eod_utc = (datetime.now(timezone.utc) + timedelta(hours=12)).strftime('%Y-%m-%dT%H:%M:%SZ')
    url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds"

    params = {
        "apiKey": API_KEY,
        "regions": REGIONS,
        "markets": MARKETS,
        "oddsFormat": ODDS_FORMAT,
        "dateFormat": DATE_FORMAT,
        "bookmakers": BOOKMAKERS,
        "commenceTimeFrom": curr_utc,
        "commenceTimeTo":eod_utc
    }

    try:
        response = requests.get(url, params=params, timeout=12)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        if 'response' in locals():
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:400]}...")
        return None

    data = response.json()

    #format data
    for game in data:
        formatted_odds_dict = {}

        home_abbr = TEAM_ABBRS.get(game["home_team"], game["home_team"][:3].upper())
        away_abbr = TEAM_ABBRS.get(game["away_team"], game["away_team"][:3].upper())
        game_name = away_abbr + ' @ ' + home_abbr
        formatted_odds_dict['game'] = game_name

        if not game["bookmakers"]:
            print("  (no FanDuel odds available for this game)")
            continue

        book = game["bookmakers"][0]  # only one


        for market in book["markets"]:
            key = market["key"]

            if key == "spreads":
                for o in market["outcomes"]:
                    team = o["name"]
                    point = o["point"]
                    price = o["price"]
                    print(f"  Spread    : {team} {point:+.1f}  @ {price:+5}")
                    formatted_odds_dict['spread'] = abs(point)
            elif key == "totals":
                for o in market["outcomes"]:
                    name = o["name"]
                    point = o["point"]
                    price = o["price"]
                    formatted_odds_dict['overUnder'] = abs(point)
                    print(f"  Total     : {name} {point:.1f}  @ {price:+5}")
        formatted_odds_list.append(formatted_odds_dict)

    # Very useful during testing / quota management
    print(f"Quota remaining this month: {response.headers.get('x-requests-remaining', 'unknown')}")
    print(f"Quota used this month      : {response.headers.get('x-requests-used', 'unknown')}")

    return formatted_odds_list


def print_games(games):
    if not games:
        print("No upcoming NBA games found (or API error)")
        return

    print(f"\nNBA upcoming games with FanDuel odds ({len(games)} found)")
    print("-" * 70)

    for game in games:
        commence = game["commence_time"]
        home = game["home_team"]
        away = game["away_team"]

        home_abbr = TEAM_ABBRS.get(game["home_team"], game["home_team"][:3].upper())
        away_abbr = TEAM_ABBRS.get(game["away_team"], game["away_team"][:3].upper())

        dt = datetime.fromisoformat(commence.replace("Z", "+00:00"))
        print(f"\n{dt:%Y-%m-%d %I:%M %p} ET  |  {away_abbr} at {home_abbr}")

        # Since we requested only FanDuel, there should be only one bookmaker
        if not game["bookmakers"]:
            print("  (no FanDuel odds available for this game)")
            continue

        book = game["bookmakers"][0]  # only one

        for market in book["markets"]:
            key = market["key"]

            if key == "h2h":
                outcomes = {o["name"]: o["price"] for o in market["outcomes"]}
                print(
                    f"  Moneyline : {away_abbr} {outcomes.get(away, 'N/A'):+5}   |   {home_abbr} {outcomes.get(home, 'N/A'):+5}")

            elif key == "spreads":
                for o in market["outcomes"]:
                    team = o["name"]
                    point = o["point"]
                    price = o["price"]
                    side = "Home" if team == home else "Away"
                    print(f"  Spread    : {team} {point:+.1f}  ({side}) @ {price:+5}")

            elif key == "totals":
                for o in market["outcomes"]:
                    name = o["name"]
                    point = o["point"]
                    price = o["price"]
                    print(f"  Total     : {name} {point:.1f}  @ {price:+5}")



def get_odds_nba_data():
    print(f"Fetching NBA odds from FanDuel only... ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
    print(f"Regions: {REGIONS} | Markets: {MARKETS} | Odds: {ODDS_FORMAT}")
    print("-" * 70)

    games = get_nba_odds()
    # if games:
    #     print_games(games)
    return games
        # Uncomment to save:
        # save_to_csv(games)