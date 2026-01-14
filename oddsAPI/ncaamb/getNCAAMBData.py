# nba_odds_pull_fanduel_only.py
# Pull current/upcoming NBA odds *only from FanDuel* using The Odds API
# Requirements: pip install requests pandas
# Get your API key → https://the-odds-api.com (free tier = 500 req/mo)

import requests
from datetime import datetime, timezone, timedelta
import pandas as pd

# ────────────────────────────────────────────────
#  CONFIGURATION
# ────────────────────────────────────────────────
API_KEY = "538fcbcd3cc38956f71965908a9df0f4"  # ← Replace with your key!

REGIONS = "us"  # usually "us" for FanDuel
MARKETS = "h2h,spreads,totals"  # moneyline, spread, total
ODDS_FORMAT = "american"  # "american" or "decimal"
DATE_FORMAT = "iso"

# Only FanDuel
BOOKMAKERS = "fanduel"

# How many days ahead to look (API usually returns ~7–14 days worth)
DAYS_AHEAD = 0

TEAM_ABBRS = {
    "Army Knights": "ARMY",
    "Holy Cross Crusaders": "HC",
    "Lehigh Mountain Hawks": "LEH",
    "Boston Univ. Terriers": "BU",
    "Chattanooga Mocs": "CHAT",
    "Wofford Terriers": "WOF",
    "East Tennessee St Buccaneers": "ETSU",
    "Western Carolina Catamounts": "WCU",
    "VCU Rams": "VCU",
    "Rhode Island Rams": "URI",
    "Butler Bulldogs": "BUT",
    "Xavier Musketeers": "XAV",
    "High Point Panthers": "HP",
    "Winthrop Eagles": "WIN",
    "Iowa Hawkeyes": "IOWA",
    "Purdue Boilermakers": "PUR",
    "Auburn Tigers": "AUB",
    "Missouri Tigers": "MIZ",
    "Niagara Purple Eagles": "NIA",
    "Canisius Golden Griffins": "CAN",
    "South Carolina Upstate Spartans": "USCU",
    "Charleston Southern Buccaneers": "CHSO",
    "Tulsa Golden Hurricane": "TLSA",
    "Charlotte 49ers": "CLT",
    "Colorado Buffaloes": "COLO",
    "Cincinnati Bearcats": "CIN",
    "Coastal Carolina Chanticleers": "CCU",
    "Marshall Thundering Herd": "MRSH",
    "Colgate Raiders": "COLG",
    "Loyola (MD) Greyhounds": "LOYMD",
    "Davidson Wildcats": "DAV",
    "GW Revolutionaries": "GW",  # George Washington
    "East Carolina Pirates": "ECU",
    "South Florida Bulls": "USF",
    "Manhattan Jaspers": "MAN",
    "Fairfield Stags": "FAIR",
    "Florida Int'l Golden Panthers": "FIU",
    "Kennesaw St Owls": "KSU",
    "Furman Paladins": "FUR",
    "Samford Bulldogs": "SAM",
    "Radford Highlanders": "RAD",
    "Gardner-Webb Bulldogs": "WEBB",
    "Ole Miss Rebels": "MISS",
    "Georgia Bulldogs": "UGA",
    "Pittsburgh Panthers": "PITT",
    "Georgia Tech Yellow Jackets": "GT",
    "Illinois St Redbirds": "ILST",
    "Indiana St Sycamores": "INST",
    "Iona Gaels": "IONA",
    "Rider Broncs": "RID",
    "Sam Houston St Bearkats": "SHSU",
    "Jacksonville St Gamecocks": "JVST",
    "Kentucky Wildcats": "UK",
    "LSU Tigers": "LSU",
    "La Salle Explorers": "LAS",
    "Richmond Spiders": "RICH",
    "UNC Asheville Bulldogs": "UNCA",
    "Presbyterian Blue Hose": "PRE",
    "Saint Peter's Peacocks": "SPC",
    "Quinnipiac Bobcats": "QUIN",
    "Sacred Heart Pioneers": "SHU",
    "Siena Saints": "SIE",
    "St. Bonaventure Bonnies": "SBU",
    "Saint Joseph's Hawks": "SJU",
    "Southern Miss Golden Eagles": "USM",
    "Troy Trojans": "TROY",
    "Lafayette Leopards": "LAF",
    "Bucknell Bison": "BUCK",
    "Middle Tennessee Blue Raiders": "MTSU",
    "Louisiana Tech Bulldogs": "LT",
    "Missouri St Bears": "MOST",
    "Western Kentucky Hilltoppers": "WKU",
    "UAB Blazers": "UAB",
    "Tulane Green Wave": "TULN",
    "Drake Bulldogs": "DRKE",
    "Southern Illinois Salukis": "SIU",
    "Fordham Rams": "FOR",
    "Saint Louis Billikens": "SLU",
    "UCF Knights": "UCF",
    "Kansas St Wildcats": "KSU",
    "Louisiana Ragin' Cajuns": "UL",
    "Texas State Bobcats": "TXST",
    "Temple Owls": "TEM",
    "Memphis Tigers": "MEM",
    "South Dakota St Jackrabbits": "SDSU",
    "North Dakota St Bison": "NDSU",
    "Rice Owls": "RICE",
    "UTSA Roadrunners": "UTSA",
    "San Diego St Aztecs": "SDSU",
    "Wyoming Cowboys": "WYO",
    "Illinois Fighting Illini": "ILL",
    "Northwestern Wildcats": "NW",
    "UCLA Bruins": "UCLA",
    "Penn State Nittany Lions": "PSU",
    "South Carolina Gamecocks": "SC",
    "Arkansas Razorbacks": "ARK",
    "Oral Roberts Golden Eagles": "ORU",
    "Denver Pioneers": "DEN",
    "North Carolina Tar Heels": "UNC",
    "Stanford Cardinal": "STAN",
    "Portland Pilots": "PORT",
    "Pepperdine Waves": "PEPP",
    "Vanderbilt Commodores": "VAN",
    "Texas Longhorns": "TEX",
    "Utah Utes": "UTAH",
    "Texas Tech Red Raiders": "TTU",
    "Virginia Tech Hokies": "VT",
    "SMU Mustangs": "SMU",
    "Loyola Marymount Lions": "LMU",
    "Oregon St Beavers": "ORST",
    "Nevada Wolf Pack": "NEV",
    "Utah State Aggies": "USU",
    "Pacific Tigers": "PAC",
    "Santa Clara Broncos": "SCU",
    "Arizona St Sun Devils": "ASU",
    "Arizona Wildcats": "ARIZ",
    "Michigan Wolverines": "MICH",
    "Washington Huskies": "WASH",
    "TCU Horned Frogs": "TCU",
    "BYU Cougars": "BYU",
    "Duke Blue Devils": "DUKE",
    "California Golden Bears": "CAL",
}

# ────────────────────────────────────────────────

def get_ncaamb_odds():
    sport_key = "basketball_ncaab"
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

    return formatted_odds_list


def print_games(games):
    if not games:
        print("No upcoming NCAA Mens Basketball games found (or API error)")
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



def get_odds_ncaamb_data():
    print(f"Fetching NCAA Mens Basketball odds from FanDuel only... ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
    print(f"Regions: {REGIONS} | Markets: {MARKETS} | Odds: {ODDS_FORMAT}")
    print("-" * 70)

    games = get_ncaamb_odds()
    # if games:
    #     print_games(games)
    return games
        # Uncomment to save:
        # save_to_csv(games)