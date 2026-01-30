import requests
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

from kalshiAPI.helpers.isExpiringToday import is_expiring_today

KALSHI_PUBLIC_BASE = "https://api.elections.kalshi.com/trade-api/v2"

SPORTS_CATEGORY = "Sports"

def fetch_all_sports_events(
    limit: int = 1000,
    status: Optional[str] = "open",
    min_close_ts: Optional[int] = None,
    with_nested_markets: bool = True,
    with_milestones: bool = False,
) -> List[Dict[str, Any]]:

    url = f"{KALSHI_PUBLIC_BASE}/events"
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
            print("Reached end of pagination.")
            break

    print(f"\nDone! Total sports events retrieved that expire TODAY: {len(all_sports_events)}")
    return all_sports_events


# ────────────────────────────────────────────────
# Example usage
# ────────────────────────────────────────────────
def getSportsEvents():
    sports_events_today = fetch_all_sports_events(
        limit=1000,
        status="open",
        with_nested_markets=True,
        with_milestones=False,
    )

    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    if not sports_events_today:
        print("No open sports events found that expire today.")
    else:
        filename = f"../kalshi/kalshiAPI/kalshi_open_sports_events.json"
        with open(filename, "w") as f:
            json.dump(sports_events_today, f, indent=2)
        return sports_events_today


