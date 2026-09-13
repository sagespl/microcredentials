from __future__ import annotations

import pandas as pd
from sklearn.pipeline import Pipeline

from src.pipelines.churn_pipeline import create_pipeline


def train_model(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    model_name: str,
    numeric_features: list[str],
    categorical_features: list[str],
) -> Pipeline:
    """
    Train churn prediction model.

    Args:
        X_train: Training features.
        y_train: Training target.
        model_name: Model identifier.
        numeric_features: Numeric feature names.
        categorical_features: Categorical feature names.

    Returns:
        Trained sklearn pipeline.
    """

    pipeline = create_pipeline(
        model_name=model_name,
        numeric_features=numeric_features,
        categorical_features=categorical_features,
    )

    pipeline.fit(
        X_train,
        y_train,
    )

    return pipeline