from kalshiAPI.helpers.createOrder import createOverUnderOrder

defaultGap = 2
nbaBasketballOverUnderGap = 2
nbaBasketballSpreadGap = 2
nbaBasketballmoneyline = 50
hockeyOverUnderGap = 1
hockeySpreadGap = 1
ncaambGap = 3

def determineGap(sport: str, type: str) -> int:
    return {
        ("nbaBasketball", "overUnder"): nbaBasketballOverUnderGap,
        ("nbaBasketball", "spread"): nbaBasketballSpreadGap,
        ("nbaBasketball", "moneyline"): nbaBasketballmoneyline,
        ("ncaambBasketball", "spread"): ncaambGap,
        ("ncaambBasketball", "overUnder"): ncaambGap,
        ("hockey", "overUnder"): hockeyOverUnderGap,
        ("hockey", "spread"): hockeySpreadGap,
    }.get((sport, type), defaultGap)


def detectGaps(kalshi, oddsAPI, sport, type):
    global oddsMetric, kalshiMetric, kalshiOutcomes, kalshiOutcomePrices, oddsOutcomes, oddsOutcomePrices
    for kalshiGame in kalshi:
        matched = False
        game_name = kalshiGame["game"]
        if type == "overUnder":
            kalshiMetric = kalshiGame["overUnder"]
        elif type == "spread":
            kalshiMetric = kalshiGame["spread"]
        elif type == "moneyline":
            kalshiOutcomePrices = kalshiGame["outcomePrices"]
            kalshiOutcomes = kalshiGame["outcomes"]

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
                elif type == "moneyline":
                    oddsOutcomePrices = odds_game["outcomePrices"]
                    oddsOutcomes = odds_game["outcomes"]

                if type == "moneyline":
                    if kalshiOutcomes[0] == oddsOutcomes[0]:
                        difference = abs(kalshiOutcomePrices[0] - oddsOutcomePrices[0])
                        kalshiMetric = kalshiOutcomePrices[0]
                        oddsMetric = oddsOutcomePrices[0]
                    elif kalshiOutcomes[0] == oddsOutcomes[1]: # handles a case where the teams are out of order
                        difference = abs(kalshiOutcomePrices[0] - oddsOutcomePrices[1])
                        kalshiMetric = kalshiOutcomePrices[0]
                        oddsMetric = oddsOutcomePrices[1]
                else:
                    difference = abs(abs(kalshiMetric) - abs(oddsMetric))


                if difference >= determineGap(sport, type):
                    print(f"Gap found for : {game_name} | {type} Kalshi : {kalshiMetric} | {type} OddsAPI : {oddsMetric}")

                    # TODO implement automatic ordering after key refresh
                    #if type == 'overUnder':
                        # create order
                        # createOverUnderOrder(kalshiGame, odds_game)
                break
        if not matched:
            print(f"No odds match found for: {game_name}")