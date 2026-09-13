from __future__ import annotations

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from src.features.encoding import create_preprocessor


def create_pipeline(
    model_name: str,
    numeric_features: list[str],
    categorical_features: list[str],
) -> Pipeline:
    """
    Create ML pipeline for churn prediction.

    Args:
        model_name: Name of ML model.
        numeric_features: Numeric feature names.
        categorical_features: Categorical feature names.

    Returns:
        sklearn Pipeline.
    """

    preprocessor = create_preprocessor(
        numeric_features=numeric_features,
        categorical_features=categorical_features,
    )

    if model_name == "logistic_regression":
        model = LogisticRegression(
            max_iter=1000,
        )

    elif model_name == "random_forest":
        model = RandomForestClassifier(
            n_estimators=200,
            random_state=42,
        )

    else:
        raise ValueError(
            f"Unknown model: {model_name}"
        )

    pipeline = Pipeline(
        steps=[
            (
                "preprocessor",
                preprocessor,
            ),
            (
                "model",
                model,
            ),
        ]
    )

    return pipeline