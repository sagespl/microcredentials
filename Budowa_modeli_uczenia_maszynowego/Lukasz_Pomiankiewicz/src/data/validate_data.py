from pathlib import Path

import pandas as pd

DATA_PATH = Path("data/raw/telco_customer_churn.csv")


REQUIRED_COLUMNS = {
    "customerID",
    "gender",
    "SeniorCitizen",
    "Partner",
    "Dependents",
    "tenure",
    "Contract",
    "MonthlyCharges",
    "TotalCharges",
    "Churn",
}


def validate_columns(df: pd.DataFrame) -> None:
    """
    Validate that required columns exist.
    """

    missing_columns = REQUIRED_COLUMNS - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )


def validate_dataset(df: pd.DataFrame) -> None:
    """
    Run dataset validation checks.
    """

    validate_columns(df)

    if df.empty:
        raise ValueError("Dataset is empty.")

    if "Churn" not in df.columns:
        raise ValueError("Target column Churn is missing.")

    print("Dataset validation passed!")


if __name__ == "__main__":
    df = pd.read_csv(DATA_PATH)

    validate_dataset(df)