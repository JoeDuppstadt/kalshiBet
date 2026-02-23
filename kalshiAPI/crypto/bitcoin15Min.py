import csv
import time

from kalshiAPI.kalshiAPI import kalshiAPI
import requests
from datetime import datetime, timedelta, timezone
import pytz
from concurrent.futures import ThreadPoolExecutor



def minutes_to_next_quarter():
    now = datetime.now()
    minute = now.minute

    remainder = minute % 15
    if remainder == 0:
        return 0
    return 15 - remainder

def get_kalshi_bitcoin_market(ticker) -> dict:
    formatted_market = {}
    url = f"https://api.elections.kalshi.com/trade-api/v2/events/{ticker}"
    response = requests.get(url=url).json()
    market = response['markets'][0]

    formatted_market['strike_price'] = market['floor_strike']
    formatted_market['yes_bid'] = market['yes_bid']
    formatted_market['no_bid'] = market['no_bid']
    formatted_market['status'] = market['status']
    formatted_market['result'] = market['result']

    return formatted_market

def get_coinbase_bitcoin_prices():
    url = "https://api.exchange.coinbase.com/products/BTC-USD/candles"

    end = datetime.now(timezone.utc)
    start = end - timedelta(minutes=4)

    params = {
        "start": start.isoformat(),
        "end": end.isoformat(),
        "granularity": 60
    }

    r = requests.get(url, params=params)
    data = r.json()

    # Coinbase returns newest first → reverse it
    #data.reverse()

    candles = []
    for c in data:
        candle = {
            "time": datetime.fromtimestamp(c[0], tz=timezone.utc),
            "low": c[1],
            "high": c[2],
            "open": c[3],
            "close": c[4],
            "volume": c[5],
            "difference": c[4] - c[3]
        }
        candles.append(candle)

    return candles

def generate_kalshi_btc_ticker():
    # Use US/Eastern timezone
    est = pytz.timezone('America/New_York')
    now = datetime.now(est)

    # Year (last two digits)
    year_short = now.strftime("%y")  # e.g. "26"

    # Month abbreviation (3 letters, uppercase)
    month_abbr = now.strftime("%b").upper()  # e.g. "FEB"

    # Day (two digits)
    day = now.strftime("%d")  # e.g. "15"

    # Current time in minutes
    current_hour = now.hour
    current_minute = now.minute
    current_total_minutes = current_hour * 60 + current_minute

    # Round UP to the next 15-minute boundary
    # This matches your examples:
    # 1415 → 1415 (already on boundary)
    # 1418 → 1430
    # 1435 → 1445
    # 1447 → 1500
    minutes_per_slot = 15
    rounded_total_minutes = ((current_total_minutes + minutes_per_slot - 1)
                             // minutes_per_slot * minutes_per_slot)

    # Convert back to hour and minute
    rounded_hour = rounded_total_minutes // 60
    rounded_minute = rounded_total_minutes % 60

    # Handle case when it rounds past midnight (very rare for 15-min market)
    if rounded_hour >= 24:
        rounded_hour -= 24
        # Note: in real usage you would typically also increment the day,
        # but Kalshi 15-min markets usually don't cross days in practice

    # Format time as four digits HHMM (military / 24-hour)
    time_str = f"{rounded_hour:02d}{rounded_minute:02d}"

    # Put it all together
    ticker = f"KXBTC15M-{year_short}{month_abbr}{day}{time_str}"
    return ticker

def get_prices(ticker):
    with ThreadPoolExecutor(max_workers=2) as executor:
        # start both at the same time
        coinbase_future = executor.submit(get_coinbase_bitcoin_prices)
        kalshi_future = executor.submit(get_kalshi_bitcoin_market, ticker)

        # wait for results
        current_bitcoin_price = coinbase_future.result()
        kalshi_market = kalshi_future.result()

    return current_bitcoin_price, kalshi_market

def save_results_to_csv(ticker: str, prediction: str, result: str, yes_bid: str, no_bid: str, ticker1, ticker2, ticker3):
    outcome = [
        [ticker, prediction, result, yes_bid, no_bid, ticker1, ticker2, ticker3],
    ]
    with open("/Users/josephduppstadt/Documents/kalshi/kalshiAPI/crypto/outcomes.csv", "a", newline="",
              encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(outcome)

def execute_order(ticker, yes_or_no):
    # code to execute order

    #check status
    finalized = False
    while not finalized:
        time.sleep(2)
        market = get_kalshi_bitcoin_market(ticker)

        if market['status'] == 'finalized':
            finalized = True
            if yes_or_no == market['result']:
                print("won")
                return market['result']
            else:
                print("lost")
                return market['result']
    return None


def start():
    kalshi = kalshiAPI()
    ticker = generate_kalshi_btc_ticker()
    minutes = minutes_to_next_quarter()

    # pause execution until the final minute of the market
    while minutes >= 3:
        minutes = minutes_to_next_quarter()
        print(f'Minutes remaining: {minutes} | Sleeping for 15 seconds')
        time.sleep(15)
    order_found = False

    # if there is 2 minutes left before market close. Start pooling
    while minutes < 3 and minutes != 0:
        minutes = minutes_to_next_quarter()
        current_bitcoin_price, kalshi_market = get_prices(ticker)

        print(ticker)
        yes_bid = kalshi_market['yes_bid']
        print(f'yes_bid: {yes_bid}')
        no_bid = kalshi_market['no_bid']
        print(f'no_bid: {no_bid}')
        print(current_bitcoin_price[0]['open'])
        print(current_bitcoin_price[1]['open'])
        print(current_bitcoin_price[2]['open'])
        print()

        if 95 <= kalshi_market['yes_bid'] < 99 and minutes < 3 and current_bitcoin_price[0]['open'] > current_bitcoin_price[1][
            'open'] > \
                current_bitcoin_price[2][
                    'open']:  # if the current yes bid is >= 99 with a minute left and the last 2 candles are going up, execute a buy order
            print("Execute yes buy")
            result = execute_order(ticker, 'yes')
            save_results_to_csv(ticker, 'yes', result, kalshi_market['yes_bid'], kalshi_market['no_bid'], current_bitcoin_price[0]['open'], current_bitcoin_price[1]['open'], current_bitcoin_price[2]['open'])
            order_found = True
            break

        elif 95 <= kalshi_market['no_bid'] < 99 and minutes < 3 and current_bitcoin_price[0]['open'] < current_bitcoin_price[1][
            'open'] < \
                current_bitcoin_price[2][
                    'open']:  # if the current no bid is >= 99 with a minute left and the last 2 candles are going down, execute a buy order
            print("Execute no buy")
            result = execute_order(ticker, 'no')
            save_results_to_csv(ticker, 'no', result, kalshi_market['yes_bid'], kalshi_market['no_bid'], current_bitcoin_price[0]['open'], current_bitcoin_price[1]['open'], current_bitcoin_price[2]['open'])

            order_found = True
            break
        time.sleep(1)
    if not order_found:
        print("No order was found:")
        print(ticker)
        print(f"yes_bid: {kalshi_market['yes_bid']}")
        print(f"no_bid: {kalshi_market['no_bid']}")
        print(f"1 Min candle open {current_bitcoin_price[0]['open']}")
        print(f"2 Min candle open {current_bitcoin_price[1]['open']}")
        print(f"3 Min candle open {current_bitcoin_price[2]['open']}")

    print("Sleeping for 5 minutes until the next market opens\n")
    time.sleep(300) # sleep for 5 minutes while the new 15 minute market is opened


if __name__ == "__main__":
    while True:
         start()
