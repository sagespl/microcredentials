from __future__ import annotations

import pandas as pd

from src.segmentation.profiling import SEGMENT_NAMES


def build_segment_explanation(
    segment: int,
    profile: pd.DataFrame,
    shap_importance: pd.DataFrame,
    top_n: int = 5,
) -> dict:
    """
    Build a business-oriented explanation for a customer segment.
    """

    segment_profile = profile[
        profile["segment"] == segment
    ]

    if segment_profile.empty:
        raise ValueError(
            f"Unknown segment: {segment}"
        )

    positive = (
        shap_importance[
            shap_importance["mean_shap"] > 0
        ]
        .sort_values(
            "mean_shap",
            ascending=False,
        )
        .head(top_n)
    )

    negative = (
        shap_importance[
            shap_importance["mean_shap"] < 0
        ]
        .sort_values(
            "mean_shap",
            ascending=True,
        )
        .head(top_n)
    )

    row = segment_profile.iloc[0]

    return {
        "segment": int(segment),
        "name": SEGMENT_NAMES.get(
            segment,
            f"Segment {segment}",
        ),
        "customers": int(row["customers"]),
        "churn_rate": float(row["churn_rate"]),
        "avg_tenure": float(row["avg_tenure"]),
        "avg_monthly_charges": float(
            row["avg_monthly_charges"]
        ),
        "avg_total_charges": float(
            row["avg_total_charges"]
        ),
        "top_churn_drivers": (
            positive[
                [
                    "feature",
                    "mean_shap",
                    "mean_abs_shap",
                ]
            ]
            .to_dict(orient="records")
        ),
        "top_churn_reducers": (
            negative[
                [
                    "feature",
                    "mean_shap",
                    "mean_abs_shap",
                ]
            ]
            .to_dict(orient="records")
        ),
    }