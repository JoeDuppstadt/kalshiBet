import os
import time
import base64
import requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from dotenv import load_dotenv

load_dotenv()  # loads .env into environment variables

# ===== CONFIG =====
API_KEY_ID = os.getenv("KALSHI_API_KEY")
PRIVATE_KEY_PATH = "/Users/josephduppstadt/Documents/kalshi/kalshiAPI/kalshikey.key"

def sign_request(timestamp: str, method: str, path: str) -> str:
    """
    Kalshi signature = base64(RSA-PSS-SHA256(timestamp + method + path))
    """
    # ===== LOAD PRIVATE KEY =====
    with open(PRIVATE_KEY_PATH, "rb") as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None,
        )

    message = f"{timestamp}{method}{path}".encode("utf-8")

    signature = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )

    return base64.b64encode(signature).decode("utf-8")