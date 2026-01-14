from kalshiAPI.helpers.createOrder import createOverUnderOrder

defaultGap = 2
basketballOverUnderGap = 2
basketballSpreadGap = 2

def determineGap(sport, type):
    if sport == "basketball" and type == "overUnder":
        return basketballOverUnderGap
    elif sport == "basketball" and type == "spread":
        return basketballOverUnderGap
    else:
        return defaultGap


def detectGaps(kalshi, oddsAPI, sport, type):
    global oddsMetric, kalshiMetric
    for kalshiGame in kalshi:
        game_name = kalshiGame["game"]
        if type == "overUnder":
            kalshiMetric = kalshiGame["overUnder"]
        elif type == "spread":
            kalshiMetric = kalshiGame["spread"]
        # Try to find matching game in oddsAPI
        for odds_game in oddsAPI:
            if odds_game.get("game") == game_name:

                if type == "overUnder":
                    oddsMetric = odds_game["overUnder"]
                elif type == "spread":
                    oddsMetric = odds_game["spread"]

                difference = abs(abs(kalshiMetric) - abs(oddsMetric))

                if difference >= determineGap(sport, type):
                    print(f"Gap found for : {game_name} | {type} Kalshi : {kalshiMetric} | {type} OddsAPI : {oddsMetric}")

                    # TODO implement automatic ordering after key refresh
                    #if type == 'overUnder':
                        # create order
                        # createOverUnderOrder(kalshiGame, odds_game)
                break
