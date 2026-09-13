import pandas as pd

from src.segmentation.kmeans import create_clustering_pipeline
from src.segmentation.profiling import profile_segments


def test_kmeans_pipeline_creates_expected_number_of_clusters():
    data = pd.DataFrame(
        {
            "SeniorCitizen": [0, 1, 0, 1, 0, 1],
            "tenure": [2, 5, 20, 25, 50, 60],
            "MonthlyCharges": [20.0, 25.0, 70.0, 75.0, 90.0, 95.0],
            "TotalCharges": [40.0, 125.0, 1400.0, 1875.0, 4500.0, 5700.0],
            "Contract": [
                "Month-to-month",
                "Month-to-month",
                "One year",
                "One year",
                "Two year",
                "Two year",
            ],
            "InternetService": [
                "DSL",
                "DSL",
                "Fiber optic",
                "Fiber optic",
                "No",
                "No",
            ],
            "PaymentMethod": [
                "Electronic check",
                "Mailed check",
                "Electronic check",
                "Mailed check",
                "Bank transfer",
                "Credit card",
            ],
        }
    )

    pipeline = create_clustering_pipeline(n_clusters=2)

    labels = pipeline.fit_predict(data)

    assert len(labels) == len(data)
    assert len(set(labels)) == 2


def test_profile_segments_returns_expected_metrics():
    data = pd.DataFrame(
        {
            "segment": [0, 0, 1, 1],
            "Churn": ["Yes", "No", "Yes", "No"],
            "tenure": [10, 20, 30, 40],
            "MonthlyCharges": [50.0, 60.0, 70.0, 80.0],
            "TotalCharges": [500.0, 1200.0, 2100.0, 3200.0],
        }
    )

    profile = profile_segments(data)

    assert list(profile["segment"]) == [0, 1]
    assert list(profile["customers"]) == [2, 2]

    assert (
        profile.loc[
            profile["segment"] == 0,
            "churn_rate",
        ].iloc[0]
        == 0.5
    )

    assert (
        profile.loc[
            profile["segment"] == 1,
            "churn_rate",
        ].iloc[0]
        == 0.5
    )

    expected_columns = {
        "segment",
        "segment_name",
        "customers",
        "churn_rate",
        "avg_tenure",
        "avg_monthly_charges",
        "avg_total_charges",
    }

    assert set(profile.columns) == expected_columns

    assert list(profile["segment_name"]) == [
        "Loyal High-Value",
        "New At-Risk",
    ]