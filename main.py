from kalshiAPI.generalAPI.getSportingEvents import getSportsEvents
from kalshiAPI.helpers.OverUnderEvents import parseOverUnderData
from kalshiAPI.helpers.SpreadEvents import parseSpreadData
from kalshiAPI.helpers.detectGaps import detectGaps
from oddsAPI.nba.getNBAData import get_odds_nba_data
from oddsAPI.ncaamb.getNCAAMBData import get_odds_ncaamb_data
from oddsAPI.nhl.getNHLData import get_odds_nhl_data

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    sportingEvents = getSportsEvents()
    #parseOverUnderData(sportingEvents, "KXNFLTOTAL")
    #parseNFLSpreadData(sportingEvents)

    # NBA
    #NBA_kalshiOverUnderData = parseOverUnderData(sportingEvents, "KXNBATOTAL")
    #NBA_kalshiSpreadData = parseSpreadData(sportingEvents, "KXNBASPREAD")
    #oddsNBAGames = get_odds_nba_data()

    # NCAAMB
    #NCAAMB_kalshiOverUnderData = parseOverUnderData(sportingEvents, "KXNCAAMBTOTAL")
    #NCAAMB_kalshiSpreadData = parseSpreadData(sportingEvents, "KXNCAAMBSPREAD")
    #oddsNCAAMBGames = get_odds_ncaamb_data()

    # NHL
    NHL_kalshiOverUnderData = parseOverUnderData(sportingEvents, "KXNHLTOTAL")
    NHL_kalshiSpreadData = parseSpreadData(sportingEvents, "KXNHLSPREAD")
    oddsNHLGames = get_odds_nhl_data()

    print("-"*70)
    print(NHL_kalshiOverUnderData)
    print(oddsNHLGames)

    # NBA detect gaps
    #detectGaps(NBA_kalshiOverUnderData, oddsNBAGames, 'basketball', 'overUnder')
    #detectGaps(NBA_kalshiSpreadData, oddsNBAGames, 'basketball', 'spread')

    # NCAAMB detect gaps
    #detectGaps(NCAAMB_kalshiOverUnderData, oddsNCAAMBGames, 'basketball', 'overUnder')
    #detectGaps(NCAAMB_kalshiSpreadData, oddsNCAAMBGames, 'basketball', 'spread')

    # nhl detect gaps
    detectGaps(NHL_kalshiOverUnderData, oddsNHLGames, 'hockey', 'overUnder')
    detectGaps(NHL_kalshiSpreadData, oddsNHLGames, 'basketball', 'spread')

