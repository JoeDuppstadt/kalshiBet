import ast
import json
from typing import Optional

import requests
from datetime import datetime, timedelta, timezone

nba_team_to_city = {
    "Raptors": "TOR",
    "Magic": "ORL",
    "Lakers":"LAL",
    "Wizards":"WAS",
    "Trail Blazers":"POR",
    "Knicks":"NYK",
    "Grizzlies":"MEM",
    "Pelicans":"NOP",
    "Kings":"SAC",
    "Celtics":"BOS",
    "Clippers":"LAC",
    "Nuggets":"DEN",
    "Cavaliers":"CLE",
    "Suns":"PHX",
    "Nets":"BKN",
    "Jazz":"UTA",
    "Pistons":"DET",
    "Warriors":"GSW",
    "Spurs":"SAS",
    "Hornets":"CHA",
    "Hawks":"ATL",
    "Pacers":"IND",
    "76ers":"PHI",
    "Heat":"MIA",
    "Timberwolves":"MIN",
    "Mavericks":"DAL",
    "Rockets":"HOU",
    "Bulls":"CHI",
}

nhl_team_to_city = {}

def current_time() -> str:
    # Current UTC time in ISO 8601 format with milliseconds
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

def hours_later(hours: int) -> str:
    # Time 'hours' later in UTC, formatted
    return (datetime.now(timezone.utc) + timedelta(hours=hours)).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

def convert_to_cities(matchup_str: str, mapping: dict) -> str:
    result = matchup_str
    for team, city in mapping.items():
        result = result.replace(team, city)
    result = result.replace('vs.', '@')
    return result



def decimal_prob_to_american(prob):
    """
    Convert a decimal probability (0.0 < prob < 1.0) to American odds.
    Returns string like '+150' or '-200'
    """
    if not 0 < prob < 1:
        return "Invalid probability"

    if prob > 0.5:
        # Favorite: negative odds
        american = -round((prob / (1 - prob)) * 100)
    else:
        # Underdog: positive odds
        american = round(((1 - prob) / prob) * 100)
    return int(american)

def get_best_line(markets):
    # Initialize
    closest_market = None
    closest_diff = float('inf')
    for market in markets:
        try:
            float_list = [float(x) for x in ast.literal_eval(market["outcomePrices"])]
        except Exception:
            continue
        over_price = float(float_list[0])
        diff = abs(over_price - 0.5)

        if diff < closest_diff:
            closest_diff = diff
            closest_market = market

    return closest_market

class PolymarketAPI:
    BASE_URL = "https://gamma-api.polymarket.com"

    def __init__(self):
        self.session = requests.Session()

    def get_markets_by_sports_market_type(self, type: str, events, sport: str):
        global game
        type_list = []
        formatted_odds_list = []
        for event in events:
            formatted_odds_dic = {}
            if event is not None:
                if sport == 'nba':
                    game = convert_to_cities(event['title'], nba_team_to_city)
                elif sport == 'nhl':
                    game = convert_to_cities(event['title'], nhl_team_to_city)
                formatted_odds_dic["game"] = game
                for market in event["markets"]:
                    if market['sportsMarketType'] == type:
                     type_list.append(market)

                bestMarket = get_best_line(type_list)
                try:
                    if type == 'totals':
                        formatted_odds_dic["overUnder"] = bestMarket['line']
                    elif type == 'spreads':
                        formatted_odds_dic["spread"] = bestMarket['line']
                    elif type == 'moneyline':
                        probs = json.loads(bestMarket['outcomePrices'])
                        probs = [decimal_prob_to_american(float(p)) for p in probs]
                        formatted_odds_dic["outcomePrices"] = probs
                        names = json.loads(bestMarket['outcomes'])
                        names = [nba_team_to_city[n] for n in names]
                        formatted_odds_dic["outcomes"] = names


                    formatted_odds_dic["id"] = bestMarket['id']
                    formatted_odds_list.append(formatted_odds_dic)
                except Exception as ex:
                    print(f"No markets for {game}: {ex}")
                type_list = []

        return formatted_odds_list

    def get_active_events(self, series_id):
        """
        Returns a list of active events from Polymarket expiring within 12 hours.
        """
        hours = 12
        url = f"{self.BASE_URL}/events?series_id={series_id}&active=true&closed=False&end_date_min={current_time()}&end_date_max={hours_later(hours)}"

        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

# Example usage:
if __name__ == "__main__":
    pm = PolymarketAPI()
    active_nba_events = pm.get_active_events('10345')
    #print(pm.get_markets_by_sports_market_type('spreads', active_nba_events))
    print(pm.get_markets_by_sports_market_type('moneyline', active_nba_events, 'nba'))
    #active_nhl_events = pm.get_active_events('10345')
    #print(pm.get_markets_by_sports_market_type('totals', active_nhl_events))


