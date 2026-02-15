import json
from typing import Dict, Any, Optional, List
from pathlib import Path
from collections import defaultdict

def find_consensus_over_under(event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
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

def parseOverUnderData(sports_events, eventPrefix):
    formatted_odds_list = []

    filtered_events = [
        event for event in sports_events
        if event.get("event_ticker", "").startswith(eventPrefix)
    ]
    if filtered_events:
        for event in filtered_events:
            formatted_odds_dict = {}

            # format data
            event["sub_title"] = event["sub_title"].replace(" at ", " @ ").split(" (")[0].strip()

            ticker = event.get("event_ticker", "—")
            title = event.get("title", "—")
            sub_title = event.get("sub_title", "—")

            consensus_market = find_consensus_over_under(event)

            if consensus_market:
                strike = consensus_market["floor_strike"]
                yes_prob = consensus_market["yes_ask"] / 100.0
                no_prob = consensus_market["no_ask"] / 100.0
                formatted_odds_dict['game'] = sub_title
                formatted_odds_dict['ticker'] = ticker
                formatted_odds_dict['overUnder'] = strike
                formatted_odds_list.append(formatted_odds_dict)

            else:
                print("  → Could not determine a clear consensus O/U line")

    else:
        print("→ No matching events found for this prefix.")

    return formatted_odds_list
