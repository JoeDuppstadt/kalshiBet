from datetime import datetime
import sys
import time
import statsapi
from kalshiAPI.kalshiAPI import kalshiAPI
from zoneinfo import ZoneInfo

def generate_market_name(away_team: str, home_team: str, game_datetime: str ):
    away_abbr = away_team.upper()[0:3]
    home_abbr = home_team.upper()[0:3]
    print(game_datetime)
    formatted_date = datetime.fromisoformat(game_datetime.replace('Z', '+00:00')) \
        .astimezone(ZoneInfo('America/New_York')) \
        .strftime('%y%b%d%H%M').upper()
    return f"KXMLBRFI-{formatted_date}{away_abbr}{home_abbr}"

kalshi_client = kalshiAPI()

while True:
    todays_games = statsapi.schedule(start_date='03/29/2026',end_date='03/29/2026')
    for game in todays_games:
        # game has over 1 run in the first inning. Attempt to place bet
        if (game.get('current_inning') == 1
                and game.get('status') == 'In Progress'
                and (game.get('away_score') > 0 or game.get('home_score') > 0)):

            event = generate_market_name(game.get('away_name'), game.get('home_name'), game.get('game_datetime'))
            print(game)
            print(event)
            # quit if event is found
            #sys.exit()

    # sleep for 1 second and check again
    time.sleep(1)








