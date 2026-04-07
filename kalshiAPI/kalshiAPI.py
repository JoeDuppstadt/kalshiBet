import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import requests
import datetime
import base64
from urllib.parse import urlparse
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding

def load_private_key():
    with open("/Users/josephduppstadt/Documents/kalshi/kalshiAPI/PROD_kalshikey.pem", "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())

class kalshiAPI:
    BASE_URL = 'https://api.elections.kalshi.com/trade-api/v2'

    def __init__(self):
        self.session = requests.Session()

    def create_signature(self, private_key, timestamp, method, path):
        """Create the request signature."""
        # Strip query parameters before signing
        path_without_query = path.split('?')[0]
        message = f"{timestamp}{method}{path_without_query}".encode('utf-8')
        signature = private_key.sign(
            message,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.DIGEST_LENGTH),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode('utf-8')

    def get_balance(self, base_url=BASE_URL):
        load_dotenv()
        api_key_id = os.getenv("PROD_KALSHI_API_KEY")
        private_key = self.load_private_key(self.PRIVATE_KEY_PATH)
        timestamp = str(int(datetime.datetime.now().timestamp() * 1000))
        path = '/portfolio/balance'
        # Signing requires the full URL path from root (e.g. /trade-api/v2/portfolio/balance)
        sign_path = urlparse(base_url + path).path
        signature = self.create_signature(private_key, timestamp, "GET", sign_path)

        headers = {
            'KALSHI-ACCESS-KEY': api_key_id,
            'KALSHI-ACCESS-SIGNATURE': signature,
            'KALSHI-ACCESS-TIMESTAMP': timestamp
        }
        response = requests.get(base_url + path, headers=headers)
        return response.json()['balance']

    def place_order(self, ticker, side, price, base_url=BASE_URL):
        buy_contact_count = 30
        load_dotenv()
        api_key_id = os.getenv("PROD_KALSHI_API_KEY")
        private_key = load_private_key()
        timestamp = str(int(datetime.datetime.now().timestamp() * 1000))
        path = '/portfolio/orders'
        sign_path = urlparse(base_url + path).path
        signature = self.create_signature(private_key, timestamp, "POST", sign_path)

        headers = {
            'KALSHI-ACCESS-KEY': api_key_id,
            'KALSHI-ACCESS-SIGNATURE': signature,
            'KALSHI-ACCESS-TIMESTAMP': timestamp,
            "Content-Type": "application/json"
        }
        if side == 'yes':
            payload = {
                "ticker": ticker,
                "side": "yes",
                "action": "buy",
                "count": buy_contact_count,
                "yes_price": 99
            }
        elif side == 'no':
            payload = {
                "ticker": ticker,
                "side": "no",
                "action": "buy",
                "count": buy_contact_count,
                "no_price": 99
            }
        response = requests.post(base_url + path, headers=headers, json=payload)
        print(response.text)

# Example usage:
if __name__ == "__main__":
    print('here')

    # kalshi = kalshiAPI()
    #
    # # Get balance
    # response = kalshi.get_balance()
    # kalshi.place_order()
    # print(response)
