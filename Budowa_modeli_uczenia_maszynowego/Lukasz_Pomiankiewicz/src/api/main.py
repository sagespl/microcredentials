from __future__ import annotations

from functools import lru_cache

import pandas as pd
import shap
from fastapi import FastAPI

from src.api.schemas import (
    CustomerData,
    PredictionFactor,
    PredictionResponse,
)
from src.data.load_data import load_data
from src.features.preprocessing import preprocess_data
from src.models.load_model import load_model
from src.models.load_segmenter import load_segmenter
from src.segmentation.profiling import SEGMENT_NAMES

app = FastAPI(
    title="Customer Churn Prediction API",
    description=(
        "API for predicting customer churn using a model from MLflow, "
        "customer segmentation and SHAP explainability."
    ),
    version="1.0.0",
)


@lru_cache(maxsize=1)
def get_models():
    """
    Load and cache both MLflow models on first use.
    """

    churn_model = load_model()
    segmenter = load_segmenter()

    return churn_model, segmenter


@lru_cache(maxsize=1)
def get_shap_explainer():
    """
    Create and cache the SHAP explainer on first use.
    """

    churn_model, _ = get_models()

    df = load_data()
    df = preprocess_data(df)

    X_background = df.drop(
        columns=["Churn"]
    ).sample(
        min(200, len(df)),
        random_state=42,
    )

    preprocessor = churn_model.named_steps["preprocessor"]
    classifier = churn_model.named_steps["model"]

    transformed_background = preprocessor.transform(
        X_background
    )

    masker = shap.maskers.Independent(
        transformed_background,
        max_samples=len(X_background),
    )

    explainer = shap.LinearExplainer(
        classifier,
        masker,
    )

    feature_names = list(
        preprocessor.get_feature_names_out()
    )

    return explainer, preprocessor, feature_names


def format_feature_name(
    feature: str,
) -> str:
    """
    Convert sklearn transformed feature names
    into human-readable labels.
    """

    if feature.startswith("num__"):
        return feature.replace(
            "num__",
            "",
            1,
        )

    if feature.startswith("cat__"):
        feature = feature.replace(
            "cat__",
            "",
            1,
        )

        if "_" in feature:
            name, value = feature.split(
                "_",
                1,
            )

            return f"{name} = {value}"

    return feature


def get_local_shap_factors(
    input_data: pd.DataFrame,
    top_n: int = 5,
) -> list[PredictionFactor]:
    """
    Calculate top user-facing local SHAP factors for one customer.

    Numeric features are always eligible.
    For one-hot encoded categorical features, only the category
    actually selected by the customer is eligible.
    """

    (
        explainer,
        preprocessor,
        feature_names,
    ) = get_shap_explainer()

    transformed_customer = preprocessor.transform(
        input_data
    )

    shap_values = explainer(
        transformed_customer
    )

    explanation = pd.DataFrame(
        {
            "feature": feature_names,
            "shap_value": shap_values.values[0],
        }
    )

    explanation["abs_shap"] = (
        explanation["shap_value"].abs()
    )

    numeric_features = set()
    categorical_features = {}

    for name, _, columns in preprocessor.transformers_:
        if name == "num":
            numeric_features.update(columns)

        elif name == "cat":
            for column in columns:
                categorical_features[column] = str(
                    input_data.iloc[0][column]
                )

    def is_user_relevant(
        feature: str,
    ) -> bool:
        if feature.startswith("num__"):
            return feature.replace(
                "num__",
                "",
                1,
            ) in numeric_features

        if feature.startswith("cat__"):
            encoded_feature = feature.replace(
                "cat__",
                "",
                1,
            )

            for column, value in categorical_features.items():
                expected_feature = (
                    f"{column}_{value}"
                )

                if encoded_feature == expected_feature:
                    return True

            return False

        return False

    explanation = explanation[
        explanation["feature"].apply(
            is_user_relevant
        )
    ]

    explanation = (
        explanation
        .sort_values(
            "abs_shap",
            ascending=False,
        )
        .head(top_n)
    )

    factors = []

    for _, row in explanation.iterrows():
        shap_value = float(
            row["shap_value"]
        )

        impact = (
            "increases_churn"
            if shap_value > 0
            else "decreases_churn"
        )

        factors.append(
            PredictionFactor(
                feature=format_feature_name(
                    row["feature"]
                ),
                impact=impact,
                shap_value=shap_value,
            )
        )

    return factors


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post(
    "/predict",
    response_model=PredictionResponse,
)
def predict_churn(
    customer: CustomerData,
):
    churn_model, segmenter = get_models()

    customer_data = customer.model_dump()

    input_data = pd.DataFrame(
        [customer_data]
    )

    prediction = churn_model.predict(
        input_data
    )[0]

    probability = churn_model.predict_proba(
        input_data
    )[0][1]

    segment = int(
        segmenter.predict(input_data)[0]
    )

    segment_name = SEGMENT_NAMES.get(
        segment,
        f"Segment {segment}",
    )

    top_factors = get_local_shap_factors(
        input_data
    )

    return PredictionResponse(
        churn_prediction=int(
            prediction
        ),
        churn_probability=float(
            probability
        ),
        segment=segment,
        segment_name=segment_name,
        top_factors=top_factors,
    )