from __future__ import annotations

import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline


def evaluate_model(
    model: Pipeline,
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> dict:
    """
    Evaluate trained classification model.

    Args:
        model: Trained sklearn pipeline.
        X_test: Test features.
        y_test: Test target.

    Returns:
        Dictionary with evaluation metrics.
    """

    y_pred = model.predict(X_test)

    y_proba = model.predict_proba(
        X_test
    )[:, 1]

    metrics = {
        "accuracy": accuracy_score(
            y_test,
            y_pred,
        ),
        "precision": precision_score(
            y_test,
            y_pred,
        ),
        "recall": recall_score(
            y_test,
            y_pred,
        ),
        "f1": f1_score(
            y_test,
            y_pred,
        ),
        "roc_auc": roc_auc_score(
            y_test,
            y_proba,
        ),
    }

    return metrics