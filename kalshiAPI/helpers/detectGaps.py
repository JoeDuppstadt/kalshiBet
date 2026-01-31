from kalshiAPI.helpers.createOrder import createOverUnderOrder

defaultGap = 2
nbaBasketballOverUnderGap = 2
nbaBasketballSpreadGap = 2
hockeyOverUnderGap = 1
hockeySpreadGap = 1
ncaambGap = 3

def determineGap(sport: str, type: str) -> int:
    return {
        ("nbaBasketball", "overUnder"): nbaBasketballOverUnderGap,
        ("nbaBasketball", "spread"): nbaBasketballSpreadGap,
        ("ncaambBasketball", "spread"): ncaambGap,
        ("ncaambBasketball", "overUnder"): ncaambGap,
        ("hockey", "overUnder"): hockeyOverUnderGap,
        ("hockey", "spread"): hockeySpreadGap,
    }.get((sport, type), defaultGap)


def detectGaps(kalshi, oddsAPI, sport, type):
    global oddsMetric, kalshiMetric
    for kalshiGame in kalshi:
        matched = False
        game_name = kalshiGame["game"]
        if type == "overUnder":
            kalshiMetric = kalshiGame["overUnder"]
        elif type == "spread":
            kalshiMetric = kalshiGame["spread"]
        # Try to find matching game in oddsAPI
        for odds_game in oddsAPI:
            if odds_game.get("game") == game_name:
                matched = True
                if type == "overUnder":
                    oddsMetric = odds_game["overUnder"]
                elif type == "spread":
                    try:
                        oddsMetric = odds_game["spread"]
                    except Exception as e:
                        print(f'No spread found for: {game_name}')

                difference = abs(abs(kalshiMetric) - abs(oddsMetric))


                if difference >= determineGap(sport, type):
                    if oddsMetric < kalshiMetric and type == 'overUnder':
                        # do not allow unders for auto ordering because overs tend to hit more
                        print(f"Under Gap found for : {game_name} | {type} Kalshi : {kalshiMetric} | {type} OddsAPI : {oddsMetric}")
                    else:
                        print(f"Gap found for : {game_name} | {type} Kalshi : {kalshiMetric} | {type} OddsAPI : {oddsMetric}")

                    # TODO implement automatic ordering after key refresh
                    #if type == 'overUnder':
                        # create order
                        # createOverUnderOrder(kalshiGame, odds_game)
                break
        if not matched:
            print(f"No odds match found for: {game_name}")