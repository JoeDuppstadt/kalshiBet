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
    "Ohio Bobcats":"OHIO",
    "Ball State Cardinals":"BALL",
    "Dayton Flyers":"DAY",
    "Loyola (Chi) Ramblers":"L-IL",
    "Tennessee Volunteers":"TENN",
    "NC State Wolfpack":"NCST",
    "UConn Huskies":"CONN",
    "Georgetown Hoyas":"GTWN",
    "Virginia Cavaliers":"UVA",
    "Mt. St. Mary's Mountaineers":"MSM",
    "Minnesota Golden Gophers":"MINN",
    "Notre Dame Fighting Irish":"ND",
    "Seton Hall Pirates":"HALL",
    "Duquesne Dukes":"DUQ",
    "Alabama Crimson Tide":"ALA",
    "Oklahoma Sooners":"OKLA",
    "Eastern Michigan Eagles":"EMU",
    "Bowling Green Falcons":"BGSU",
    "Buffalo Bulls":"BUFF",
    "Miami (OH) RedHawks":"MOH",
    "Wagner Seahawks":"Wagner",
    "New Haven Chargers": "New Haven",
    "Ohio State Buckeyes": "OSU",
    "Western Michigan Broncos": "WMU",
    "Akron Zips": "AKR",
    "Bradley Braves": "BRAD",
    "Columbia Lions": "CLMB",
    "Brown Bears": "BRWN",
    "Central Connecticut St Blue Devils": "CCSU",
    "St. Francis (PA) Red Flash": "St. Francis (PA)",
    "Stonehill Skyhawks":"STNH",
    "Florida A&M Rattlers":"FAMU",
    "Le Moyne Dolphins": "LMC",
    "Chicago St Cougars": "Chicago St.",
    "Iowa State Cyclones": "ISU",
    "Nebraska Cornhuskers": "NEB",
    "Coppin St Eagles": "COPP",
    "Maryland-Eastern Shore Hawks": "UMES",
    "Morgan St Bears": "MORG",
    "Delaware St Hornets": "DSU",
    "East Texas A&M Lions": "ETAM",
    "Houston Christian Huskies": "HCU",
    "Howard Bison": "NOW",
    "North Carolina Central Eagles": "NCCU",
    "Norfolk St Spartans": "NORF",
    "George Mason Patriots":"GMU",
    "Yale Bulldogs":"YALE",
    "Alabama St Hornets":"ALST",
    "South Carolina St Bulldogs": "SCST",
    "SE Louisiana Lions": "SELA",
    "Texas A&M-CC Islanders": "Texas A&M-Corpus Christi",
    "Southern Jaguars": "Southern University",
    "Cornell Big Red":"COR",
    "Harvard Crimson":"HARV",
    "Grambling St Tigers": "Grambling St.",
    "Northwestern St Demons": "NWST",
    "Incarnate Word Cardinals": "IW",
    "UNLV Rebels": "UNLA",
    "San José St Spartans": "SJSU",
    "UC Irvine Anteaters": "UCI",
    "Marquette Golden Eagles":"MARQ",
    "DePaul Blue Demons":"DEP",
    "Colorado St Rams":"CSU",
    "Boise State Broncos":"BSU",
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
    "Missouri Tigers": "MIZZ",
    "Niagara Purple Eagles": "NIAG",
    "Canisius Golden Griffins": "CAN",
    "South Carolina Upstate Spartans": "USCU",
    "Charleston Southern Buccaneers": "CHSO",
    "Tulsa Golden Hurricane": "TLSA",
    "Charlotte 49ers": "CHAR",
    "Colorado Buffaloes": "COLO",
    "Cincinnati Bearcats": "CIN",
    "Coastal Carolina Chanticleers": "CCAR",
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
    "Kennesaw St Owls": "KENN",
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
    "Marist Red Foxes":"MRST",
    "Hampton Pirates":"HAMP",
    "Siena Saints": "SIE",
    "St. Bonaventure Bonnies": "SBU",
    "Saint Joseph's Hawks": "SJU",
    "Southern Miss Golden Eagles": "USM",
    "Troy Trojans": "TROY",
    "Lafayette Leopards": "LAF",
    "Bucknell Bison": "BUCK",
    "Middle Tennessee Blue Raiders": "MTU",
    "Louisiana Tech Bulldogs": "LT",
    "Missouri St Bears": "MOSU",
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
    "South Dakota St Jackrabbits": "SDST",
    "North Dakota St Bison": "NDSU",
    "Rice Owls": "RICE",
    "UTSA Roadrunners": "UTSA",
    "San Diego St Aztecs": "SDSU",
    "Wyoming Cowboys": "WYO",
    "Illinois Fighting Illini": "ILL",
    "Northwestern Wildcats": "NW",
    "UCLA Bruins": "UCLA",
    "Penn State Nittany Lions": "PSU",
    "South Carolina Gamecocks": "SCAR",
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
    "UMBC Retrievers": "UMBC",
    "Bryant Bulldogs": "BRY",
    "New Mexico St Aggies": "NMSU",
    "Liberty Flames": "LIB",
    "Mercer Bears": "MER",
    "VMI Keydets": "VMI",
    "NJIT Highlanders": "NJIT",
    "UMass Lowell River Hawks": "MASSL",
    "Binghamton Bearcats": "BING",
    "Albany Great Danes": "ALBY",
    "Austin Peay Governors":"PEAY",
    "James Madison Dukes": "JMU",
    "Appalachian St Mountaineers": "APP",
    "Robert Morris Colonials": "RMU",
    "IUPUI Jaguars": "IUPUI",
    "Green Bay Phoenix": "GB",
    "Cleveland St Vikings": "CSU",
    "Boston College Eagles":"BC",
    "Syracuse Orange":"SYR",
    "UTEP Miners": "UTEP",
    "Delaware Blue Hens": "DEL",
    "Detroit Mercy Titans": "DET",
    "Northern Kentucky Norse": "NKU",
    "Drexel Dragons": "DREX",
    "Monmouth Hawks": "MONM",
    "Elon Phoenix": "ELON",
    "Northeastern Huskies": "NEU",
    "Queens University Royals": "QUC",
    "Murray St Racers":"MURR",
    "Navy Midshipmen":"NAVY",
    "Wisconsin Badgers":"WIS",
    "Florida Gulf Coast Eagles": "FGCU",
    "Old Dominion Monarchs": "ODU",
    "Georgia Southern Eagles": "GASO",
    "Hofstra Pride": "HOF",
    "Stony Brook Seawolves": "SBU",
    "Maine Black Bears": "ME",
    "Vermont Catamounts": "UVM",
    "Oakland Golden Grizzlies": "OAK",
    "Milwaukee Panthers": "MILW",
    "North Florida Ospreys": "UNF",
    "North Alabama Lions": "UNA",
    "North Carolina A&T Aggies": "NCAT",
    "William & Mary Tribe": "WM",
    "West Georgia Wolves": "UWG",
    "Stetson Hatters": "STET",
    "The Citadel Bulldogs": "CIT",
    "UNC Greensboro Spartans": "UNCG",
    "Youngstown St Penguins": "YSU",
    "Wright St Raiders": "WRST",
    "Jacksonville Dolphins": "JAC",
    "Central Arkansas Bears": "UCA",
    "Cal Baptist Lancers": "CBU",
    "Abilene Christian Wildcats": "AC",
    "Arkansas St Red Wolves": "ARST",
    "South Alabama Jaguars": "USA",
    "Eastern Illinois Panthers": "EIU",
    "Arkansas-Little Rock Trojans": "UALR",
    "Eastern Kentucky Colonels": "EKY",
    "New Hampshire Wildcats":"UNH",
    "PEAY": "APSU",
    "Bellarmine Knights": "BELL",
    "Lipscomb Bisons": "LIP",
    "Charleston Cougars": "COFC",
    "Towson Tigers": "TOWS",
    "St. Thomas (MN) Tommies": "STMN",
    "Princeton Tigers":"PRIN",
    "North Dakota Fighting Hawks": "UND",
    "UMKC Kangaroos": "UMKC",
    "South Dakota Coyotes": "SDAK",
    "Morehead St Eagles": "MORE",
    "Tennessee St Tigers": "TNST",
    "SIU-Edwardsville Cougars": "SIUE",
    "Tenn-Martin Skyhawks": "UTM",
    "Southern Indiana Screaming Eagles": "USI",
    "Tennessee Tech Golden Eagles": "TNTC",
    "Tarleton State Texans": "TARL",
    "Southern Utah Thunderbirds": "SUU",
    "CSU Fullerton Titans": "CSUF",
    "UC Davis Aggies": "UCD",
    "Eastern Washington Eagles": "EWU",
    "Weber State Wildcats": "WEB",
    "Wichita St Shockers": "WICH",
    "Florida Atlantic Owls": "FAU",
    "Idaho Vandals": "IDHO",
    "Idaho State Bengals": "IDST",
    "Lindenwood Lions": "LINW",
    "SE Missouri St Redhawks": "SEMO",
    "UT-Arlington Mavericks": "UTA",
    "Utah Tech Trailblazers": "UTU",
    "UC Santa Barbara Gauchos": "UCSB",
    "CSU Bakersfield Roadrunners": "CSUB",
    "CSU Northridge Matadors": "CSUN",
    "UC San Diego Tritons": "UCSD",
    "Hawai'i Rainbow Warriors": "HAW",
    "Cal Poly Mustangs": "CP",
    "Gonzaga Bulldogs": "GONZ",
    "Washington St Cougars": "WSU",
    "UC Riverside Highlanders": "UCR",
    "Long Beach St 49ers": "LBSU",
    "N Colorado Bears": "UNC",
    "Portland St Vikings": "PRST",
    "Northern Arizona Lumberjacks": "NAU",
    "Sacramento St Hornets": "SAC",
    "San Diego Toreros": "USD",
    "Seattle Redhawks": "SEA",
    "Creighton Bluejays": "CREI",
    "Providence Friars": "PROV",
    "Toledo Rockets": "TOL",
    "Kent State Golden Flashes": "KENT",
    "Baylor Bears": "BAY",
    "Kansas Jayhawks": "KU",
    "Miami Hurricanes":"MIA",
    "Clemson Tigers": "CLEM",
    "Indiana Hoosiers": "IND",
    "Grand Canyon Antelopes": "GC",
    "Longwood Lancers": "LONG",
    "Pennsylvania Quakers": "PENN",
    "Dartmouth Big Green": "DART",
    "UIC Flames": "UIC",
    "Massachusetts Minutemen": "MASS",
    "Northern Illinois Huskies": "NIU",
    "Merrimack Warriors": "MRMK",
    "Northern Iowa Panthers": "UNI",
    "Valparaiso Beacons": "VALP",
    "Georgia St Panthers":"GAST",
    "UL Monroe Warhawks": "ULM",
    "Air Force Falcons": "AFA",
    "Texas Southern Tigers": "Texas Southern",
    "Alcorn St Braves": "ALCN",
    "Western Illinois Leathernecks": "WIU",
    "Prairie View Panthers": "PV",
    "Jackson St Tigers": "JKST",
    "Lamar Cardinals": "LAM",
    "Nicholls St Colonels": "NICH",
    "Utah Valley Wolverines": "UVU",
    "Oregon Ducks'": "ORE",
    "McNeese Cowboys": "MCNS",
    "UT Rio Grande Valley Vaqueros": "UTRGV",
    "Bethune-Cookman Wildcats": "COOK",
    "Miss Valley St Delta Devils": "MVSU",
    "Wake Forest Demon Deacons": "WAKE",
    "Florida St Seminoles": "FSU",
    "Michigan St Spartans": "MSU",
    "Stephen F. Austin Lumberjacks": "SFA",
    "New Orleans Privateers": "UNO",
    "Texas A&M Aggies": "TXAM",
    "West Virginia Mountaineers": "WVU",
    "Oklahoma St Cowboys":"OKST",
    "Montana St Bobcats":"MTST",
    "Montana Grizzlies": "MONT",
    "Mississippi St Bulldogs": "MSST",
    "Louisville Cardinals": "LOU",
    "Villanova Wildcats": "VILL",
    "St. John's Red Storm": "SJU",
    "Omaha Mavericks": "NEOM",
    "New Mexico Lobos": "UNM",
    "Saint Mary's Gaels": "SMC",
    "Fairleigh Dickinson Knights": "FDU",
    "LIU Sharks": "LIU",
    "UNC Wilmington Seahawks": "UNCW",
    "Campbell Fighting Camels": "CAMP",
    "Belmont Bruins": "BEL",
    "Fresno St Bulldogs": "FRES",
    "High Point Panthers": "HP",
    "USC Trojans": "USC",
    "Maryland Terrapins": "MD",
    "American Eagles": "AMER",
    "Fort Wayne Mastodons": "PFW",
    "North Texas Mean Green": "UNT",
    "Houston Cougars": "HOU",
    "San Francisco Dons": "SF",
    "Central Michigan Chippewas": "CMU",
    "Florida Gators": "FLA",
    "Evansville Purple Aces": "EVAN",
    "Rutgers Scarlet Knights": "RUTG",
    "Oregon Ducks":"ORE"

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
        #"commenceTimeFrom": curr_utc,
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
                    formatted_odds_dict['spread'] = abs(point)
            elif key == "totals":
                for o in market["outcomes"]:
                    name = o["name"]
                    point = o["point"]
                    price = o["price"]
                    formatted_odds_dict['overUnder'] = abs(point)
        formatted_odds_list.append(formatted_odds_dict)

    saveKeyUsage(apiKeyName, response.headers.get('x-requests-remaining', 'unknown'))

    return formatted_odds_list


def print_games(games):
    if not games:
        print("No upcoming NCAA Mens Basketball games found (or API error)")
        return

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

    games = get_ncaamb_odds()
    # if games:
    #     print_games(games)
    return games
        # Uncomment to save:
        # save_to_csv(games)