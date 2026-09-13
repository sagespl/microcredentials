from __future__ import annotations

import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import silhouette_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

NUMERIC_FEATURES = [
    "SeniorCitizen",
    "tenure",
    "MonthlyCharges",
    "TotalCharges",
]

CATEGORICAL_FEATURES = [
    "Contract",
    "InternetService",
    "PaymentMethod",
]

RANDOM_STATE = 42


def create_clustering_pipeline(n_clusters: int) -> Pipeline:
    numeric_transformer = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(strategy="median"),
        ),
        (
            "scaler",
            StandardScaler(),
        ),
    ]
)

    categorical_transformer = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(strategy="most_frequent"),
        ),
        (
            "onehot",
            OneHotEncoder(
                handle_unknown="ignore",
                sparse_output=False,
            ),
        ),
    ]
)

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "num",
                numeric_transformer,
                NUMERIC_FEATURES,
            ),
            (
                "cat",
                categorical_transformer,
                CATEGORICAL_FEATURES,
            ),
        ]
    )

    return Pipeline(
        steps=[
            (
                "preprocessor",
                preprocessor,
            ),
            (
                "kmeans",
                KMeans(
                    n_clusters=n_clusters,
                    random_state=RANDOM_STATE,
                    n_init=10,
                ),
            ),
        ]
    )


def evaluate_k(
    X: pd.DataFrame,
    k: int,
) -> float:
    pipeline = create_clustering_pipeline(k)

    transformed = pipeline.named_steps["preprocessor"].fit_transform(X)

    labels = pipeline.named_steps["kmeans"].fit_predict(transformed)

    return silhouette_score(
        transformed,
        labels,
    )


def run_segmentation(
    df: pd.DataFrame,
    min_k: int = 2,
    max_k: int = 6,
):
    X = df[
        NUMERIC_FEATURES + CATEGORICAL_FEATURES
    ].copy()

    scores = {}

    for k in range(min_k, max_k + 1):
        score = evaluate_k(
            X=X,
            k=k,
        )
        scores[k] = score

    best_k = max(
        scores,
        key=scores.get,
    )

    model = create_clustering_pipeline(
        n_clusters=best_k,
    )

    labels = model.fit_predict(X)

    segmented_df = df.copy()
    segmented_df["segment"] = labels

    mlflow.log_param(
        "task",
        "customer_segmentation",
    )
    mlflow.log_param(
        "best_k",
        best_k,
    )

    for k, score in scores.items():
        mlflow.log_metric(
            f"silhouette_k_{k}",
            score,
        )

    mlflow.log_metric(
        "best_silhouette_score",
        scores[best_k],
    )

    mlflow.sklearn.log_model(
    model,
    name="kmeans_model",
    registered_model_name="customer-segmentation-model",
    skops_trusted_types=["numpy.dtype"],
    )

    return (
        model,
        segmented_df,
        scores,
    )

