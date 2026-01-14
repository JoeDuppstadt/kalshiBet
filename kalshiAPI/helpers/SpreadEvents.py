import json
from typing import Dict, Any, Optional, List
from pathlib import Path


def find_consensus_spread(event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Finds the spread line closest to 50% implied probability (using yes_ask as proxy).
    Returns the best market dict or None if no suitable market found.
    """
    markets = event.get("markets", [])
    if not markets:
        return None

    def distance_to_fifty(m):
        return abs(m.get("yes_ask", 0) / 100.0 - 0.5)

    best = min(markets, key=distance_to_fifty, default=None)
    if best is None:
        return None

    # Sanity check: if it's way off 50%, it's probably not the main spread line
    prob = best["yes_ask"] / 100.0
    if abs(prob - 0.5) > 0.28:  # slightly tighter than O/U since spreads are usually sharper
        return None

    return best


def parseSpreadData(sports_events, eventPrefix):
    formatted_odds_list = []

    filtered_events = [
        event for event in sports_events
        if event.get("event_ticker", "").startswith(eventPrefix)
    ]

    print(f"\nFound {len(filtered_events)} spread events starting with '{eventPrefix}'")

    if not filtered_events:
        print("→ No matching spread events found for this prefix.")
        return

    for event in filtered_events:
        formatted_odds_dict = {}

        event["sub_title"] = event["sub_title"].replace(" at ", " @ ").split(" (")[0].strip()

        ticker = event.get("event_ticker", "—")
        title = event.get("title", "—")           # usually "Team A vs Team B"
        sub_title = event.get("sub_title", "—")   # often contains date / time

        print(f"\n{'─' * 70}")
        print(f"Game: {title}")
        print(f"  Ticker:      {ticker}")
        print(f"  Sub-title:   {sub_title}")

        consensus_market = find_consensus_spread(event)

        if consensus_market:
            strike = consensus_market["floor_strike"]
            yes_ask_cents = consensus_market.get("yes_ask", 0)
            no_ask_cents = consensus_market.get("no_ask", 0)
            yes_prob = yes_ask_cents / 100.0
            no_prob = no_ask_cents / 100.0

            # Try to determine direction (which side is the favorite)
            # Many platforms set "Yes = favorite covers" or "Yes = team listed first covers"
            # You may need to adjust this logic based on your actual data convention
            side_hint = ""
            if " @ " in title or " vs " in title:
                parts = title.replace(" @ ", " vs ").split(" vs ")
                if len(parts) == 2:
                    away, home = parts
                    if strike < 0:
                        side_hint = f" ({away} {strike:+.1f})"
                    elif strike > 0:
                        side_hint = f" ({home} {strike:+.1f})"

            formatted_odds_dict['game'] = sub_title
            formatted_odds_dict['ticker'] = ticker
            formatted_odds_dict['spread'] = abs(strike)
            formatted_odds_list.append(formatted_odds_dict)

            print(f"  → Current consensus spread: **{strike:+.1f}**{side_hint}")
            print(f"     Yes ask ({strike:+.1f}):  {yes_prob:5.1%}  ({yes_ask_cents}¢)")
            print(f"     No  ask ({-strike:+.1f}):  {no_prob:5.1%}  ({no_ask_cents}¢)")

            # Optional: show implied edge / value
            if abs(yes_prob - 0.5) < 0.05:
                print("     → Very balanced line (sharp)")
            elif yes_prob > 0.60 or no_prob > 0.60:
                print("     → Line appears skewed / possible value on the other side")
        else:
            print("  → Could not determine a clear consensus spread line")
    return formatted_odds_list