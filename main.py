from kalshiAPI.generalAPI.getSportingEvents import getSportsEvents
from kalshiAPI.helpers.OverUnderEvents import parseOverUnderData
from kalshiAPI.helpers.SpreadEvents import parseSpreadData
from kalshiAPI.helpers.detectGaps import detectGaps
from oddsAPI.nba.getNBAData import get_odds_nba_data
from oddsAPI.ncaamb.getNCAAMBData import get_odds_ncaamb_data

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    sportingEvents = getSportsEvents()
    #parseOverUnderData(sportingEvents, "KXNFLTOTAL")
    #parseNFLSpreadData(sportingEvents)

    #NBA_kalshiOverUnderData = parseOverUnderData(sportingEvents, "KXNBATOTAL")
    #NBA_kalshiSpreadData = parseSpreadData(sportingEvents, "KXNBASPREAD")
    #oddsNBAGames = get_odds_nba_data()

    NCAAMB_kalshiOverUnderData = parseOverUnderData(sportingEvents, "KXNCAAMBTOTAL")
    #print(parseOverUnderData(sportingEvents, "KXNCAAMBTOTAL-26JAN14TEMMEM"))
    oddsNCAAMBGames = get_odds_ncaamb_data()

    print("-"*70)

    # NBA
    #detectGaps(NBA_kalshiOverUnderData, oddsNBAGames, 'basketball', 'overUnder')
    #detectGaps(NBA_kalshiSpreadData, oddsNBAGames, 'basketball', 'spread')

    # NCAAMB
    detectGaps(NCAAMB_kalshiOverUnderData, oddsNCAAMBGames, 'basketball', 'overUnder')
