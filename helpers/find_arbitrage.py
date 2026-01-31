# ---------- ODDS CONVERSIONS ----------

def american_to_prob(odds):
    odds = float(odds)
    if odds > 0:
        return 100 / (odds + 100)
    else:
        return abs(odds) / (abs(odds) + 100)


def american_to_decimal(odds):
    odds = float(odds)
    if odds > 0:
        return 1 + (odds / 100)
    else:
        return 1 + (100 / abs(odds))


# ---------- BET SIZING ----------

def calculate_bets(odds1, odds2, bankroll):
    d1 = american_to_decimal(odds1)
    d2 = american_to_decimal(odds2)

    inv1 = 1 / d1
    inv2 = 1 / d2

    bet1 = bankroll * (inv1 / (inv1 + inv2))
    bet2 = bankroll - bet1

    payout = bet1 * d1  # same for both outcomes
    profit = payout - bankroll
    roi = (profit / bankroll) * 100

    return round(bet1, 2), round(bet2, 2), round(profit, 2), round(roi, 2)


# ---------- ARBITRAGE FINDER ----------

def find_arbitrage(kalshi, polymarket, bankroll=1000, min_edge=0.01):
    """
    min_edge = 0.01 means 1% minimum edge filter
    """
    arbs = []

    for kGame in kalshi:
        for pmGame in polymarket:

            # Match same event
            if kGame['game'] != pmGame['game']:
                continue

            k_prices = dict(zip(kGame['outcomes'], kGame['outcomePrices']))
            pm_prices = dict(zip(pmGame['outcomes'], pmGame['outcomePrices']))

            if set(k_prices.keys()) != set(pm_prices.keys()):
                continue

            team1, team2 = list(k_prices.keys())

            # Convert to probabilities
            k_p1 = american_to_prob(k_prices[team1])
            k_p2 = american_to_prob(k_prices[team2])
            pm_p1 = american_to_prob(pm_prices[team1])
            pm_p2 = american_to_prob(pm_prices[team2])

            # ----- Case 1 -----
            total_prob_1 = k_p1 + pm_p2
            edge_1 = 1 - total_prob_1

            if edge_1 > min_edge:
                bet1, bet2, profit, roi = calculate_bets(
                    k_prices[team1], pm_prices[team2], bankroll
                )

                arbs.append({
                    "game": kGame['game'],
                    "bet_1": f"{team1} on Kalshi @ {k_prices[team1]}",
                    "bet_2": f"{team2} on Polymarket @ {pm_prices[team2]}",
                    "bet_sizes": {
                        "bet_1_amount": bet1,
                        "bet_2_amount": bet2
                    },
                    "guaranteed_profit": profit,
                    "roi_percent": roi
                })

            # ----- Case 2 -----
            total_prob_2 = pm_p1 + k_p2
            edge_2 = 1 - total_prob_2

            if edge_2 > min_edge:
                bet1, bet2, profit, roi = calculate_bets(
                    pm_prices[team1], k_prices[team2], bankroll
                )

                arbs.append({
                    "game": kGame['game'],
                    "bet_1": f"{team1} on Polymarket @ {pm_prices[team1]}",
                    "bet_2": f"{team2} on Kalshi @ {k_prices[team2]}",
                    "bet_sizes": {
                        "bet_1_amount": bet1,
                        "bet_2_amount": bet2
                    },
                    "guaranteed_profit": profit,
                    "roi_percent": roi
                })

    return arbs
