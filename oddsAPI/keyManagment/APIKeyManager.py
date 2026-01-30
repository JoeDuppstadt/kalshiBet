import csv
from typing import Dict, Tuple
from dotenv import load_dotenv
import os

load_dotenv()  # loads .env into environment variables

CSV_PATH = "oddsAPI/keyManagment/keysRemaining.csv"

def saveKeyUsage(key: str, keysRemaining: str) -> None:
    data: Dict[str, str] = {}

    # 1. Read existing CSV if it exists
    if os.path.exists(CSV_PATH):
        with open(CSV_PATH, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                data[row["key"]] = row["keysRemaining"]

    # 2. Upsert
    data[key] = keysRemaining

    # 3. Write back entire CSV
    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["key", "keysRemaining"]
        )
        writer.writeheader()

        for k, v in data.items():
            writer.writerow({
                "key": k,
                "keysRemaining": v
            })

def returnAPIKey() -> Tuple[str, str]:
    # 1. Read existing CSV if it exists
    if os.path.exists(CSV_PATH):
        with open(CSV_PATH, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if int(row['keysRemaining']) > 2:
                    return row['key'], os.getenv(row['key'])
    raise Exception("No API keys have keysRemaining > 0")
