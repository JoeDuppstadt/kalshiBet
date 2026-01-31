from helpers.find_arbitrage import find_arbitrage
from kalshiAPI.helpers.OverUnderEvents import parseOverUnderData
from kalshiAPI.helpers.SpreadEvents import parseSpreadData
from kalshiAPI.helpers.detectGaps import detectGaps
from kalshiAPI.kalshiAPI import kalshiAPI
from oddsAPI.nba.getNBAData import get_odds_nba_data
from oddsAPI.ncaamb.getNCAAMBData import get_odds_ncaamb_data
from oddsAPI.nhl.getNHLData import get_odds_nhl_data
from polymarketAPI.polymarketAPI import PolymarketAPI

nbaSeason = True
ncaambSeason = False
nhlSeason = False
if __name__ == '__main__':
    kalshi = kalshiAPI()
    pm = PolymarketAPI()
    sportingEvents = kalshi.fetch_all_sports_events(
        limit=1000,
        status="open",
        with_nested_markets=True,
        with_milestones=False,
    )

    # NBA
    if nbaSeason:
        #find arbitrage before anything else
        basketballId = '10345'
        active_nba_events = pm.get_active_events(basketballId)
        polyMarket_NBAMoneyline = pm.get_markets_by_sports_market_type('moneyline', active_nba_events, 'nba')
        NBA_kalshiMoneylineData = kalshi.get_markets_by_sports_market_type('moneyline', sportingEvents, 'nba', 'KXNBAGAME')
        print(find_arbitrage(NBA_kalshiMoneylineData, polyMarket_NBAMoneyline))

        NBA_kalshiOverUnderData = kalshi.parseOverUnderData(sportingEvents, "KXNBATOTAL")
        NBA_kalshiSpreadData = kalshi.parseSpreadData(sportingEvents, "KXNBASPREAD")
        oddsNBAGames = get_odds_nba_data()

        print('\n------------------------------KalshiNBA------------------------------------------------------------------------------------------------------------------')
        print(NBA_kalshiOverUnderData)
        print(oddsNBAGames)
        detectGaps(NBA_kalshiOverUnderData, oddsNBAGames, 'nbaBasketball', 'overUnder')
        detectGaps(NBA_kalshiSpreadData, oddsNBAGames, 'nbaBasketball', 'spread')

        print('\n------------------------------PolymarketNBA------------------------------------------------------------------------------------------------------------------')
        print(polyMarket_NBAMoneyline)
        detectGaps(polyMarket_NBAMoneyline, oddsNBAGames, 'nbaBasketball', 'moneyline')


        if nhlSeason:
            NHL_kalshiOverUnderData = parseOverUnderData(sportingEvents, "KXNHLTOTAL")
            NHL_kalshiSpreadData = parseSpreadData(sportingEvents, "KXNHLSPREAD")
            oddsNHLGames = get_odds_nhl_data()

            print('\n------------------------------KalshiNHL------------------------------------------------------------------------------------------------------------------')
            print(NHL_kalshiOverUnderData)
            print(oddsNHLGames)
            # nhl detect gaps
            detectGaps(NHL_kalshiOverUnderData, oddsNHLGames, 'hockey', 'overUnder')
            detectGaps(NHL_kalshiSpreadData, oddsNHLGames, 'hockey', 'spread')

            print('\n------------------------------PolymarketNHL------------------------------------------------------------------------------------------------------------------')
            nhlId = '10346'
            active_nhl_events = pm.get_active_events(nhlId)
            polyMarket_NHLOverUnder = pm.get_markets_by_sports_market_type('totals', active_nhl_events, 'nhl')
            polyMarket_NHLSpreads = pm.get_markets_by_sports_market_type('spreads', active_nhl_events, 'nhl')
            print(polyMarket_NHLOverUnder)
            print(polyMarket_NHLSpreads)
            detectGaps(polyMarket_NHLOverUnder, oddsNHLGames, 'hockey', 'overUnder')
            detectGaps(polyMarket_NHLSpreads, oddsNHLGames, 'hockey', 'spread')

    # # NCAAMB
    if ncaambSeason:
        NCAAMB_kalshiOverUnderData = parseOverUnderData(sportingEvents, "KXNCAAMBTOTAL")
        NCAAMB_kalshiSpreadData = parseSpreadData(sportingEvents, "KXNCAAMBSPREAD")
        oddsNCAAMBGames = get_odds_ncaamb_data()

        print('\n------------------------------KalshiNCAAMB----------------------------------------------------------------------------------------------------------------')
        print(NCAAMB_kalshiOverUnderData)
        print(oddsNCAAMBGames)
        # NCAAMB detect gaps
        if NCAAMB_kalshiOverUnderData is not None:
            detectGaps(NCAAMB_kalshiOverUnderData, oddsNCAAMBGames, 'ncaambBasketball', 'overUnder')
        if NCAAMB_kalshiSpreadData is not None:
            detectGaps(NCAAMB_kalshiSpreadData, oddsNCAAMBGames, 'ncaambBasketball', 'spread')






