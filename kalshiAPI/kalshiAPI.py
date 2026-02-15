import sys
import time

import requests
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta

from kalshiAPI.helpers.OverUnderEvents import parseOverUnderData
from kalshiAPI.helpers.SpreadEvents import parseSpreadData


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
# Example usage:
if __name__ == "__main__":
    kalshi = kalshiAPI()
    sportingEvents = kalshi.fetch_all_sports_events(
        limit=1000,
        status="open",
        with_nested_markets=True,
        with_milestones=False,
    )
    NBA_overUnderEvents = kalshi.get_markets_by_sports_market_type('overUnder', sportingEvents, 'nba', 'KXNBATOTAL')
    print(kalshi.get_best_odds(NBA_overUnderEvents))

