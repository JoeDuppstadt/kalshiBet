from kalshiAPI.generalAPI.getSportingEvents import getSportsEvents
from kalshiAPI.helpers.OverUnderEvents import parseOverUnderData
from kalshiAPI.helpers.SpreadEvents import parseSpreadData
from kalshiAPI.helpers.detectGaps import detectGaps
from oddsAPI.nba.getNBAData import get_odds_nba_data
from oddsAPI.ncaamb.getNCAAMBData import get_odds_ncaamb_data
from oddsAPI.nhl.getNHLData import get_odds_nhl_data
from polymarketAPI.polymarketAPI import PolymarketAPI

nbaSeason = True
ncaambSeason = True
nhlSeason = True
if __name__ == '__main__':
    sportingEvents = getSportsEvents()
    #parseOverUnderData(sportingEvents, "KXNFLTOTAL")
    #parseNFLSpreadData(sportingEvents)

    # NBA
    if nbaSeason:
        NBA_kalshiOverUnderData = parseOverUnderData(sportingEvents, "KXNBATOTAL")
        NBA_kalshiSpreadData = parseSpreadData(sportingEvents, "KXNBASPREAD")
        oddsNBAGames = get_odds_nba_data()
        print('\n------------------------------KalshiNBA------------------------------------------------------------------------------------------------------------------')
        print(NBA_kalshiOverUnderData)
        print(oddsNBAGames)
        detectGaps(NBA_kalshiOverUnderData, oddsNBAGames, 'basketball', 'overUnder')
        detectGaps(NBA_kalshiSpreadData, oddsNBAGames, 'basketball', 'spread')

        basketballId = '10345'
        pm = PolymarketAPI()
        active_nba_events = pm.get_active_events(basketballId)

        print('\n------------------------------PolymarketNBA------------------------------------------------------------------------------------------------------------------')
        polyMarket_NBAOverUnder = pm.get_markets_by_sports_market_type('totals', active_nba_events)
        polyMarket_NBASpreads = pm.get_markets_by_sports_market_type('spreads', active_nba_events)
        print(polyMarket_NBAOverUnder)
        print(polyMarket_NBASpreads)
        detectGaps(polyMarket_NBAOverUnder, oddsNBAGames, 'basketball', 'overUnder')
        detectGaps(polyMarket_NBASpreads, oddsNBAGames, 'basketball', 'spread')

        if nhlSeason:
            NHL_kalshiOverUnderData = parseOverUnderData(sportingEvents, "KXNHLTOTAL")
            NHL_kalshiSpreadData = parseSpreadData(sportingEvents, "KXNHLSPREAD")
            oddsNHLGames = get_odds_nhl_data()

            print('\n------------------------------KalshiNHL------------------------------------------------------------------------------------------------------------------')
            print(NHL_kalshiOverUnderData)
            print(oddsNHLGames)
            # nhl detect gaps
            detectGaps(NHL_kalshiOverUnderData, oddsNHLGames, 'hockey', 'overUnder')
            detectGaps(NHL_kalshiSpreadData, oddsNHLGames, 'basketball', 'spread')

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
            detectGaps(NCAAMB_kalshiOverUnderData, oddsNCAAMBGames, 'basketball', 'overUnder')
        if NCAAMB_kalshiSpreadData is not None:
            detectGaps(NCAAMB_kalshiSpreadData, oddsNCAAMBGames, 'basketball', 'spread')






