from __future__ import annotations

import os

import mlflow
from sklearn.pipeline import Pipeline

MODEL_NAME = "customer-segmentation-model"
MODEL_VERSION = "1"


def load_segmenter(
    model_name: str = MODEL_NAME,
    model_version: str = MODEL_VERSION,
) -> Pipeline:
    """
    Load the customer segmentation pipeline from MLflow Model Registry.
    """

    tracking_uri = os.getenv("MLFLOW_TRACKING_URI")

    if tracking_uri:
        mlflow.set_tracking_uri(tracking_uri)

    model_uri = f"models:/{model_name}/{model_version}"

    return mlflow.sklearn.load_model(model_uri)