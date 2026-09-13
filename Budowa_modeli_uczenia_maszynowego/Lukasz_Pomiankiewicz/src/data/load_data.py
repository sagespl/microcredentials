from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = PROJECT_ROOT / "data" / "raw" / "telco_customer_churn.csv"


def load_data() -> pd.DataFrame:
    """
    Load customer churn dataset.

    Returns:
        pandas DataFrame containing customer data.
    """

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_PATH}. "
            "Run download_data.py first."
        )

    return pd.read_csv(DATA_PATH)


if __name__ == "__main__":
    df = load_data()

    print("Dataset loaded successfully!")
    print()

    print(f"Shape: {df.shape}")
    print()

    print(df.head())