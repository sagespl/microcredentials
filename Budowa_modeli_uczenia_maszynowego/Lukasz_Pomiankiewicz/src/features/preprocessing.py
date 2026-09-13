from __future__ import annotations

import numpy as np
import pandas as pd


def replace_hidden_missing_values(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Replace hidden missing values with NaN.
    """

    df = df.copy()

    df = df.replace(" ", np.nan)

    return df


def convert_total_charges(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Convert TotalCharges column to numeric.
    """

    df = df.copy()

    df["TotalCharges"] = pd.to_numeric(
        df["TotalCharges"],
        errors="coerce",
    )

    return df


def remove_customer_id(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Remove customer identifier.
    """

    df = df.copy()

    if "customerID" in df.columns:
        df = df.drop(columns=["customerID"])

    return df


def preprocess_data(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Run preprocessing pipeline.
    """

    df = replace_hidden_missing_values(df)
    df = convert_total_charges(df)
    df = remove_customer_id(df)

    return df