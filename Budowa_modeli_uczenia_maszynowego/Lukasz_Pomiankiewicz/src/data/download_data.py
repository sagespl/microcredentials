from pathlib import Path

import requests

DATASET_URL = (
    "https://raw.githubusercontent.com/treselle-systems/"
    "customer_churn_analysis/master/WA_Fn-UseC_-Telco-Customer-Churn.csv"
)

DATA_DIR = Path("data/raw")
OUTPUT_FILE = DATA_DIR / "telco_customer_churn.csv"


def download_dataset() -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if OUTPUT_FILE.exists():
        print(f"Dataset already exists: {OUTPUT_FILE}")
        return OUTPUT_FILE

    print("Downloading dataset...")

    response = requests.get(DATASET_URL, timeout=30)
    response.raise_for_status()

    OUTPUT_FILE.write_bytes(response.content)

    print(f"Dataset saved: {OUTPUT_FILE}")

    return OUTPUT_FILE


if __name__ == "__main__":
    download_dataset()