import requests
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import os

from oddsAPI.keyManagment.APIKeyManager import saveKeyUsage, returnAPIKey

# ────────────────────────────────────────────────
#  CONFIGURATION
# ────────────────────────────────────────────────

load_dotenv()  # loads .env into environment variables

apiKeyName, API_KEY = returnAPIKey()

REGIONS = "us"  # usually "us" for FanDuel
MARKETS = "h2h,spreads,totals"  # moneyline, spread, total
ODDS_FORMAT = "american"  # "american" or "decimal"
DATE_FORMAT = "iso"

# Only FanDuel
BOOKMAKERS = "fanduel"

# How many days ahead to look (API usually returns ~7–14 days worth)
DAYS_AHEAD = 0

TEAM_ABBRS = {
    "Dallas Stars": "DAL",
    "Tampa Bay Lightning":"TB",
    "Ottawa Senators":"OTT",
    "Detroit Red Wings": "DET",
    "St Louis Blues": "STL",
    "Edmonton Oilers": "EDM",
    "Washington Capitals": "WSH",
    "Colorado Avalanche": "COL",
    "Pittsburgh Penguins": "PIT",
    "Seattle Kraken": "SEA",
    "San Jose Sharks": "SJ",
    "Florida Panthers": "FLA",
    "Minnesota Wild": "MIN",
    "Toronto Maple Leafs": "TOR",
    "Philadelphia Flyers": "PHI",
    "Vegas Golden Knights": "VGK",
    "Winnipeg Jets": "WPG",
    "Chicago Blackhawks": "CHI",
    "New Jersey Devils": "NJ",
    "Calgary Flames": "CGY",
    "New York Rangers": "NYR",
    "Anaheim Ducks": "ANA",
    "New York Islanders": "NYI",
    "Vancouver Canucks": "VAN",
    "Buffalo Sabres": "BUF",
    "Nashville Predators": "NSH",
    "Boston Bruins": "BOS",
    "Columbus Blue Jackets": "CBJ",
    "Montréal Canadiens": "MTL",
    "Los Angeles Kings": "LA",
    "Utah Mammoth":"UTA",
    "Carolina Hurricanes":"CAR"
}

# ────────────────────────────────────────────────

def get_nhl_odds():
    sport_key = "icehockey_nhl"
    formatted_odds_list = []


    curr_utc = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    eod_utc = (datetime.now(timezone.utc) + timedelta(hours=14)).strftime('%Y-%m-%dT%H:%M:%SZ')
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

        home_abbr = TEAM_ABBRS.get(game["home_team"], game["home_team"])
        away_abbr = TEAM_ABBRS.get(game["away_team"], game["away_team"])
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

    saveKeyUsage(apiKeyName, response.headers.get('x-requests-remaining', 'unknown'))

    return formatted_odds_list

def get_odds_nhl_data():
    print(f"Fetching NHL odds from FanDuel only... ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
    print(f"Regions: {REGIONS} | Markets: {MARKETS} | Odds: {ODDS_FORMAT}")
    print("-" * 70)

    games = get_nhl_odds()
    return games
