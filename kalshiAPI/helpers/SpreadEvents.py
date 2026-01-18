import json
from typing import Dict, Any, Optional, List
from pathlib import Path


def find_consensus_spread(event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Returns the single Kalshi market whose YES/NO prices imply the
    closest true 50/50 Over/Under consensus.
    """

    markets = event.get("markets", [])
    if not markets:
        return None

    best_market = None
    best_score = float("inf")

    for m in markets:
        if not isinstance(m, dict):
            continue

        yes_ask = m.get("yes_ask")
        no_ask = m.get("no_ask")
        total = m.get("floor_strike")

        if yes_ask is None or no_ask is None or total is None:
            continue

        p_over = yes_ask / 100.0
        p_under = no_ask / 100.0

        # Reject broken books
        if not (0.05 <= p_over <= 0.95 and 0.05 <= p_under <= 0.95):
            continue

        score = (
            abs(p_over - 0.5) +
            abs(p_under - 0.5) +
            abs((p_over + p_under) - 1.0)
        )

        if score < best_score:
            best_score = score
            best_market = m

    return best_market


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