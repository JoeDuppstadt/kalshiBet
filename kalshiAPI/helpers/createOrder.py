import sys
from typing import Dict, Any
from kalshiAPI.generalAPI.getOrders import get_orders


def searchBeforeCreate(ticker: str) -> bool:
    orders = get_orders()
    for order in orders:
        #print(order['ticker'])
        #print(ticker)
        if order['ticker'].rsplit("-", 1)[0] == ticker:
            return True
        else:
            return False

def createOverUnderOrder(kalshiGame: Dict[str, Any], odds_game: Dict[str, Any]) -> Dict[str, Any]:
    if kalshiGame["overUnder"] > odds_game["overUnder"]:
        print(searchBeforeCreate(kalshiGame["ticker"]))
        print('Bet No')
    elif kalshiGame["overUnder"] < odds_game["overUnder"]:
        print(searchBeforeCreate(kalshiGame["ticker"]))
        print('Bet Yes')
    else:
        print('Issue with detecting gaps')
        sys.exit(1)