import time
import requests
from kalshiAPI.generalAPI.signIn import sign_request, API_KEY_ID

BASE_URL = "https://api.elections.kalshi.com"
PATH = "/trade-api/v2/portfolio/balance"
URL = BASE_URL + PATH

def get_balance():
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
    return response.json()


if __name__ == "__main__":
    balance = get_balance()

    # Values are in CENTS
    print("Raw response:", balance)
    print(f"Cash balance: ${balance['balance'] / 100:.2f}")
    print(f"Portfolio value: ${balance['portfolio_value'] / 100:.2f}")
