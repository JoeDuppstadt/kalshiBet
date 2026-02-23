import json
import os
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
import base64
import requests
from kalshi_python_sync import Configuration, KalshiClient, CreateOrderRequest
import uuid
from dotenv import load_dotenv

from helpers.decimal_to_america_odds import decimal_prob_to_american
from kalshiAPI.helpers.SpreadEvents import parseSpreadData
#from helpers.SpreadEvents import parseSpreadData

def is_expiring_today(expiration_str: Optional[str]) -> bool:
    """
    Returns True if the expiration timestamp is considered "today" in a practical sense:
    - Either on the current UTC date, OR
    - In the first 6 hours of the next UTC date (i.e. up to 06:00 UTC the next day)

    This is useful for systems where "today's" items can expire shortly into the next day.
    """
    if not expiration_str:
        return False

    try:
        # Parse ISO 8601 string → aware datetime
        # Handles both Z and ±00:00 style
        dt = datetime.fromisoformat(expiration_str.replace("Z", "+00:00"))

        # Current time in UTC
        now_utc = datetime.now(timezone.utc)

        # Start of today (00:00 UTC)
        today_start = now_utc.replace(hour=0, minute=0, second=0, microsecond=0)

        # Cutoff = tomorrow 06:00 UTC
        cutoff = today_start + timedelta(days=1, hours=6)

        # Expires "today" if it's between today 00:00 and tomorrow 06:00
        return today_start <= dt < cutoff

    except (ValueError, TypeError):
        return False

class kalshiAPI:
    BASE_URL = "https://api.elections.kalshi.com"

    def __init__(self):
        self.session = requests.Session()


    def get_best_odds(self, events: List[Dict[str, Any]], bet_type: str) -> List[Dict[str, Any]]:
        formatted_odds_list = []
        for event in events:
            closest_to_50 = {}
            game_name = event['sub_title'].replace(" at ", " @ ").split(" (")[0].strip()

            closest_market = min(event['markets'], key=lambda x: abs(x['yes_ask'] - 50))

            if 70 > closest_market['yes_ask'] > 30:
                closest_to_50['game'] = game_name
                if bet_type == 'overUnder':
                    closest_to_50['overUnder'] = closest_market['floor_strike']
                elif bet_type == 'spread':
                    print('spread here')
                closest_to_50['no_ask'] = closest_market['no_ask']
                closest_to_50['yes_ask'] = closest_market['yes_ask']
                formatted_odds_list.append(closest_to_50)
            else:
                print(f"Yes odds for {game_name} are greater than 70 or less than 30")
        return formatted_odds_list

    def get_markets_by_sports_market_type(self, type: str, sports_events, sport: str, eventPrefix: str):
        filtered_events = [
            event for event in sports_events
            if event.get("event_ticker", "").startswith(eventPrefix)
        ]
        return filtered_events

    def get_markets_by_crypto_market_type(self, crypto_events, eventPrefix: str):
        filtered_events = [
            event for event in crypto_events
            if event.get("event_ticker", "").startswith(eventPrefix)
        ]
        return filtered_events

    def parseOverUnderData(self, sportingEvents, sportLeague, eventPrefix):
        events = self.get_markets_by_sports_market_type('overUnder', sportingEvents, sportLeague, eventPrefix)
        return self.get_best_odds(events, 'overUnder')

    def parseMoneyLineData(self, sportingEvents, sportLeague, eventPrefix):
        events = self.get_markets_by_sports_market_type('moneyline', sportingEvents, sportLeague, eventPrefix)

        formatted_odds_list = []
        for event in events:
            game_json = {}
            outcomes = []
            outcomePrices = []

            game_json['game'] = event['title']
            for market in event['markets']:
                outcomes.append(market['yes_sub_title'])
                outcomePrices.append(decimal_prob_to_american(int(market['yes_ask']) / 100))

            game_json['outcomes'] = outcomes
            game_json['outcomePrices'] = outcomePrices
            formatted_odds_list.append(game_json)
        return formatted_odds_list


    def parseSpreadData(self, sportingEvents, eventPrefix):
        return parseSpreadData(sportingEvents, "KXNBASPREAD")

    def fetch_all_sports_events(self, limit: int = 1000, status: Optional[str] = "open", min_close_ts: Optional[int] = None, with_nested_markets: bool = True, with_milestones: bool = False) -> List[Dict[str, Any]]:
        SPORTS_CATEGORY = "Sports"

        PATH = 'trade-api/v2/events'
        url = f"{self.BASE_URL}/{PATH}"
        headers = {"Accept": "application/json"}

        params: Dict[str, Any] = {
            "limit": min(max(limit, 1), 200),
            "with_nested_markets": str(with_nested_markets).lower(),
            "with_milestones": str(with_milestones).lower(),
        }

        if status:
            params["status"] = status
        if min_close_ts is not None:
            params["min_close_ts"] = min_close_ts

        all_sports_events: List[Dict[str, Any]] = []
        cursor: Optional[str] = None
        page_count = 0

        while True:
            page_count += 1

            if cursor:
                params["cursor"] = cursor

            response = requests.get(url, headers=headers, params=params, timeout=15)
            response.raise_for_status()

            data = response.json()
            page_events = data.get("events", [])

            # Filter for sports + expires today
            sports_today = [
                event for event in page_events
                if event.get("category") == SPORTS_CATEGORY
                   and event.get("markets")  # exists and is not empty
                   and is_expiring_today(event["markets"][0].get("expected_expiration_time"))
            ]
            all_sports_events.extend(sports_today)

            cursor = data.get("cursor")
            if not cursor:
                break

        print(f"\nDone! Total sports events retrieved that expire TODAY: {len(all_sports_events)}")

        try:
            with open('/Users/josephduppstadt/Documents/kalshi/kalshiAPI/kalshi_open_sports_events.json', 'w', encoding='utf-8') as output_file:
                json.dump(all_sports_events, output_file, ensure_ascii=False, indent=4)
        except IOError as e:
            print(f"Error writing to file: {e}")

        return all_sports_events

    def fetch_all_crypto_events(self, limit: int = 1000, status: Optional[str] = "open", min_close_ts: Optional[int] = None, with_nested_markets: bool = True, with_milestones: bool = False) -> List[Dict[str, Any]]:
        SPORTS_CATEGORY = "Crypto"

        PATH = 'trade-api/v2/events'
        url = f"{self.BASE_URL}/{PATH}"
        headers = {"Accept": "application/json"}

        params: Dict[str, Any] = {
            "limit": min(max(limit, 1), 200),
            "with_nested_markets": str(with_nested_markets).lower(),
            "with_milestones": str(with_milestones).lower(),
        }

        if status:
            params["status"] = status
        if min_close_ts is not None:
            params["min_close_ts"] = min_close_ts

        all_crypto_events: List[Dict[str, Any]] = []
        cursor: Optional[str] = None
        page_count = 0

        while True:
            page_count += 1

            if cursor:
                params["cursor"] = cursor

            response = requests.get(url, headers=headers, params=params, timeout=15)
            response.raise_for_status()

            data = response.json()
            page_events = data.get("events", [])

            # Filter for sports + expires today
            crypto_today = [
                event for event in page_events
                if event.get("category") == SPORTS_CATEGORY
                   and event.get("markets")  # exists and is not empty
                   and is_expiring_today(event["markets"][0].get("expected_expiration_time"))
            ]
            all_crypto_events.extend(crypto_today)

            cursor = data.get("cursor")
            if not cursor:
                break
        return all_crypto_events

    def closeOrder(self, client, orderId: str):
        client.closeOrder(orderId)

    def createAPIClient(self):
        load_dotenv()

        host = None
        private_key_path = None
        api_key = None
        environment = os.getenv('ENVIRONMENT')

        if environment == 'DEV':
            host = "https://demo-api.kalshi.co/trade-api/v2"
            private_key_path = "/Users/josephduppstadt/Documents/kalshi/kalshiAPI/DEV_kalshikey.pem"
            api_key = os.getenv("DEV_KALSHI_API_KEY")
        elif environment == 'PROD':
            host = "https://api.kalshi.com"
            private_key_path = "/Users/josephduppstadt/Documents/kalshi/kalshiAPI/PROD_kalshikey.pem"
            api_key = os.getenv("PROD_KALSHI_API_KEY")

        config = Configuration(
            host=host
        )

        with open(private_key_path, "r") as f:
            private_key = f.read()

        config.api_key_id = api_key
        config.private_key_pem = private_key

        return KalshiClient(config)
# Example usage:
if __name__ == "__main__":
    kalshi = kalshiAPI()

    client = kalshi.createAPIClient()

    try:
        response = client.create_order(
            ticker="KXMARSVRAIL-50",
            action="buy",
            side="yes",
            count=1,
            type="limit",
            yes_price=50,
            client_order_id=str(uuid.uuid4())
        )
        order_id = getattr(response, 'order_id', getattr(response.order, 'order_id', 'Unknown'))
        print(f"Order placed! Order ID: {order_id}")

    except Exception as e:
        print(f"Failed to place order: {e}")