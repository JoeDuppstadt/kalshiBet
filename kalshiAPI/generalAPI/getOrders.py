import time
import requests
from kalshiAPI.generalAPI.signIn import sign_request, API_KEY_ID

BASE_URL = "https://api.elections.kalshi.com"
PATH = "/trade-api/v2/portfolio/orders"
URL = BASE_URL + PATH
def get_orders(ticker=None):
    method = "GET"
    timestamp = str(int(time.time() * 1000))  # milliseconds
    signature = sign_request(timestamp, method, PATH)

    headers = {
        "KALSHI-ACCESS-KEY": API_KEY_ID,
        "KALSHI-ACCESS-TIMESTAMP": timestamp,
        "KALSHI-ACCESS-SIGNATURE": signature,
        "Accept": "application/json",
    }

    response = requests.get(URL, headers=headers)
    response.raise_for_status()

    return response.json()['orders']


if __name__ == "__main__":
    orders = get_orders()
