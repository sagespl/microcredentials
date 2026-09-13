from __future__ import annotations

import pandas as pd

SEGMENT_NAMES = {
    0: "Loyal High-Value",
    1: "New At-Risk",
    2: "Established At-Risk",
    3: "Low-Cost Stable",
}


def profile_segments(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a business-oriented profile for each customer segment.

    Segment names are interpretive labels assigned after analysing
    the characteristics and churn behaviour of each cluster.
    """

    profile = (
        df.groupby("segment")
        .agg(
            customers=("segment", "size"),
            churn_rate=(
                "Churn",
                lambda x: (x == "Yes").mean(),
            ),
            avg_tenure=("tenure", "mean"),
            avg_monthly_charges=("MonthlyCharges", "mean"),
            avg_total_charges=("TotalCharges", "mean"),
        )
        .reset_index()
    )

    profile["segment_name"] = (
        profile["segment"].map(SEGMENT_NAMES)
    )

    return profile[
        [
            "segment",
            "segment_name",
            "customers",
            "churn_rate",
            "avg_tenure",
            "avg_monthly_charges",
            "avg_total_charges",
        ]
    ]