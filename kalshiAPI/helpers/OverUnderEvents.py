import json
from typing import Dict, Any, Optional, List
from pathlib import Path
from collections import defaultdict

def find_consensus_over_under(event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Returns the single Kalshi market whose prices imply the
    closest true 50/50 Over/Under consensus using mid prices.
    """

    markets = event.get("markets", [])
    if not markets:
        return None

    best_market = None
    best_score = float("inf")

    for m in markets:
        if not isinstance(m, dict):
            continue

        yes_bid = m.get("yes_bid")
        yes_ask = m.get("yes_ask")
        no_bid = m.get("no_bid")
        no_ask = m.get("no_ask")
        total = m.get("floor_strike")

        if None in (yes_bid, yes_ask, no_bid, no_ask, total):
            continue

        # Mid prices → implied probabilities
        yes_mid = (yes_bid + yes_ask) / 200.0
        no_mid = (no_bid + no_ask) / 200.0

        # Reject broken or illiquid books
        if yes_mid <= 0 or no_mid <= 0:
            continue

        # Renormalize so probabilities sum to 1
        p_over = yes_mid / (yes_mid + no_mid)
        p_under = no_mid / (yes_mid + no_mid)

        # Distance from true 50/50 consensus
        score = abs(p_over - 0.5)

        if score < best_score:
            best_score = score
            best_market = m

    return best_market

def parseOverUnderData(sports_events, eventPrefix):
    formatted_odds_list = []

    filtered_events = [
        event for event in sports_events
        if event.get("event_ticker", "").startswith(eventPrefix)
    ]

    print(f"\nFound {len(filtered_events)} events starting with '{eventPrefix}'")

    if filtered_events:
        for event in filtered_events:
            formatted_odds_dict = {}

            # format data
            event["sub_title"] = event["sub_title"].replace(" at ", " @ ").split(" (")[0].strip()

            ticker = event.get("event_ticker", "—")
            title = event.get("title", "—")
            sub_title = event.get("sub_title", "—")

            print(f"\n{'─' * 70}")
            print(f"Game: {title}")
            print(f"  Ticker:      {ticker}")
            print(f"  Sub-title:   {sub_title}")

            consensus_market = find_consensus_over_under(event)

            if consensus_market:
                strike = consensus_market["floor_strike"]
                yes_prob = consensus_market["yes_ask"] / 100.0
                no_prob = consensus_market["no_ask"] / 100.0

                formatted_odds_dict['game'] = sub_title
                formatted_odds_dict['ticker'] = ticker
                formatted_odds_dict['overUnder'] = strike
                formatted_odds_list.append(formatted_odds_dict)

                print(f"  → Current consensus O/U: **{strike}**")
                print(f"     Over {strike}:  Yes ask {yes_prob:.1%} ({consensus_market['yes_ask_dollars']})")
                print(f"     Under {strike}: No ask  {no_prob:.1%} ({consensus_market['no_ask_dollars']})")

            else:
                print("  → Could not determine a clear consensus O/U line")

    else:
        print("→ No matching events found for this prefix.")

    return formatted_odds_list