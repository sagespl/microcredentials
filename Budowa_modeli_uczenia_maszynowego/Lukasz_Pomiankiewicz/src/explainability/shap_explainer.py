from __future__ import annotations

import pandas as pd
import shap

from src.data.load_data import load_data
from src.features.preprocessing import preprocess_data
from src.models.load_model import load_model
from src.segmentation.kmeans import (
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    create_clustering_pipeline,
)

BEST_K = 4


def create_shap_explainer(
    model,
    background_data: pd.DataFrame,
) -> shap.LinearExplainer:
    """
    Create a SHAP LinearExplainer for the Logistic Regression model.
    """

    preprocessor = model.named_steps["preprocessor"]
    classifier = model.named_steps["model"]

    transformed_background = preprocessor.transform(
        background_data
    )

    masker = shap.maskers.Independent(
        transformed_background,
        max_samples=len(background_data),
    )

    return shap.LinearExplainer(
        classifier,
        masker,
    )


def get_feature_names(model) -> list[str]:
    """
    Get feature names after preprocessing.
    """

    preprocessor = model.named_steps["preprocessor"]

    return list(
        preprocessor.get_feature_names_out()
    )


def calculate_global_importance(
    model,
    X: pd.DataFrame,
    background_size: int = 200,
) -> pd.DataFrame:
    """
    Calculate global mean absolute SHAP importance.
    """

    preprocessor = model.named_steps["preprocessor"]

    background_data = X.sample(
        min(background_size, len(X)),
        random_state=42,
    )

    transformed_X = preprocessor.transform(X)

    explainer = create_shap_explainer(
        model=model,
        background_data=background_data,
    )

    shap_values = explainer(
        transformed_X
    )

    importance = pd.DataFrame(
        {
            "feature": get_feature_names(model),
            "mean_abs_shap": (
                abs(shap_values.values)
                .mean(axis=0)
            ),
        }
    )

    return (
        importance
        .sort_values(
            "mean_abs_shap",
            ascending=False,
        )
        .reset_index(drop=True)
    )


def explain_customer(
    model,
    customer: pd.DataFrame,
    background_data: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate SHAP contributions for a single customer.
    """

    preprocessor = model.named_steps["preprocessor"]

    transformed_customer = preprocessor.transform(
        customer
    )

    explainer = create_shap_explainer(
        model=model,
        background_data=background_data,
    )

    shap_values = explainer(
        transformed_customer
    )

    explanation = pd.DataFrame(
        {
            "feature": get_feature_names(model),
            "shap_value": shap_values.values[0],
        }
    )

    explanation["abs_shap"] = (
        explanation["shap_value"].abs()
    )

    return (
        explanation
        .sort_values(
            "abs_shap",
            ascending=False,
        )
        .reset_index(drop=True)
    )


def assign_segments(
    df: pd.DataFrame,
) -> pd.Series:
    """
    Assign customers to the selected KMeans segments.
    """

    segmentation_features = df[
        NUMERIC_FEATURES + CATEGORICAL_FEATURES
    ].copy()

    clustering_pipeline = create_clustering_pipeline(
        n_clusters=BEST_K,
    )

    labels = clustering_pipeline.fit_predict(
        segmentation_features
    )

    return pd.Series(
        labels,
        index=df.index,
        name="segment",
    )


def calculate_segment_importance(
    model,
    X: pd.DataFrame,
    segments: pd.Series,
    background_size: int = 200,
) -> dict[int, pd.DataFrame]:
    """
    Calculate signed and absolute SHAP importance separately
    for each customer segment.

    The same Champion model and SHAP background are used for
    every segment so the results remain comparable.
    """

    preprocessor = model.named_steps["preprocessor"]

    background_data = X.sample(
        min(background_size, len(X)),
        random_state=42,
    )

    transformed_X = preprocessor.transform(X)

    explainer = create_shap_explainer(
        model=model,
        background_data=background_data,
    )

    shap_values = explainer(
        transformed_X
    )

    feature_names = get_feature_names(model)

    segment_importance: dict[int, pd.DataFrame] = {}

    for segment in sorted(
        segments.unique()
    ):
        segment_mask = (
            segments == segment
        ).to_numpy()

        segment_shap_values = (
            shap_values.values[segment_mask]
        )

        importance = pd.DataFrame(
            {
                "feature": feature_names,
                "mean_shap": (
                    segment_shap_values
                    .mean(axis=0)
                ),
                "mean_abs_shap": (
                    abs(segment_shap_values)
                    .mean(axis=0)
                ),
            }
        )

        segment_importance[int(segment)] = (
            importance
            .sort_values(
                "mean_abs_shap",
                ascending=False,
            )
            .reset_index(drop=True)
        )

    return segment_importance


def print_segment_drivers(
    segment: int,
    importance: pd.DataFrame,
    top_n: int = 5,
) -> None:
    """
    Print the strongest positive and negative SHAP drivers
    for a segment.
    """

    print(
        f"\nSegment {segment} - top churn drivers:"
    )

    positive = (
        importance[
            importance["mean_shap"] > 0
        ]
        .sort_values(
            "mean_shap",
            ascending=False,
        )
        .head(top_n)
    )

    if positive.empty:
        print("No positive churn drivers found.")
    else:
        print(
            positive.to_string(
                index=False
            )
        )

    print(
        f"\nSegment {segment} - top churn reducers:"
    )

    negative = (
        importance[
            importance["mean_shap"] < 0
        ]
        .sort_values(
            "mean_shap",
            ascending=True,
        )
        .head(top_n)
    )

    if negative.empty:
        print("No negative churn drivers found.")
    else:
        print(
            negative.to_string(
                index=False
            )
        )


def main():
    model = load_model()

    df = load_data()
    df = preprocess_data(df)

    X = df.drop(
        columns=["Churn"]
    )

    # ---------------------------------------------------------
    # Global SHAP
    # ---------------------------------------------------------

    print("\nGlobal SHAP importance:")

    global_importance = calculate_global_importance(
        model=model,
        X=X,
    )

    print(
        global_importance.head(20).to_string(
            index=False
        )
    )

    # ---------------------------------------------------------
    # Segment assignment
    # ---------------------------------------------------------

    segments = assign_segments(df)

    print("\nSegment sizes:")

    print(
        segments.value_counts()
        .sort_index()
    )

    # ---------------------------------------------------------
    # Segment-specific SHAP
    # ---------------------------------------------------------

    segment_importance = calculate_segment_importance(
        model=model,
        X=X,
        segments=segments,
    )

    for segment, importance in (
        segment_importance.items()
    ):
        print(
            f"\nSegment {segment} SHAP importance:"
        )

        print(
            importance.head(10).to_string(
                index=False
            )
        )

        print_segment_drivers(
            segment=segment,
            importance=importance,
            top_n=5,
        )

    # ---------------------------------------------------------
    # Local SHAP
    # ---------------------------------------------------------

    customer = pd.DataFrame(
        [
            {
                "gender": "Female",
                "SeniorCitizen": 0,
                "Partner": "No",
                "Dependents": "No",
                "tenure": 2,
                "PhoneService": "Yes",
                "MultipleLines": "No",
                "InternetService": "Fiber optic",
                "OnlineSecurity": "No",
                "OnlineBackup": "No",
                "DeviceProtection": "No",
                "TechSupport": "No",
                "StreamingTV": "No",
                "StreamingMovies": "No",
                "Contract": "Month-to-month",
                "PaperlessBilling": "Yes",
                "PaymentMethod": "Electronic check",
                "MonthlyCharges": 70.35,
                "TotalCharges": 140.70,
            }
        ]
    )

    background_data = X.sample(
        min(200, len(X)),
        random_state=42,
    )

    local_explanation = explain_customer(
        model=model,
        customer=customer,
        background_data=background_data,
    )

    print("\nLocal SHAP explanation:")

    print(
        local_explanation.head(15).to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()