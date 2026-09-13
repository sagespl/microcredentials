import pandas as pd
from fastapi.testclient import TestClient

from src.api.main import app, get_models, get_shap_explainer

client = TestClient(app)


class MockChurnModel:
    def predict(self, X: pd.DataFrame):
        return [1]

    def predict_proba(self, X: pd.DataFrame):
        return [[0.3072, 0.6928]]


class MockSegmenter:
    def predict(self, X: pd.DataFrame):
        return [1]


class MockExplanation:
    def __init__(self):
        self.values = [[
            1.6270,
            -0.5004,
            0.3328,
            0.2607,
            0.2046,
        ]]


class MockExplainer:
    def __call__(self, X):
        return MockExplanation()


class MockPreprocessor:
    def transform(self, X):
        return X

    def get_feature_names_out(self):
        return [
            "num__tenure",
            "num__TotalCharges",
            "cat__InternetService_Fiber optic",
            "cat__Contract_Month-to-month",
            "cat__Contract_Two year",
        ]

    @property
    def transformers_(self):
        return [
            (
                "num",
                None,
                [
                    "tenure",
                    "TotalCharges",
                ],
            ),
            (
                "cat",
                None,
                [
                    "InternetService",
                    "Contract",
                ],
            ),
        ]


def mock_get_models():
    return MockChurnModel(), MockSegmenter()


def mock_get_shap_explainer():
    return (
        MockExplainer(),
        MockPreprocessor(),
        [
            "num__tenure",
            "num__TotalCharges",
            "cat__InternetService_Fiber optic",
            "cat__Contract_Month-to-month",
            "cat__Contract_Two year",
        ],
    )


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok"
    }


def test_predict():
    from src.api import main

    original_get_models = main.get_models
    original_get_shap_explainer = main.get_shap_explainer

    main.get_models = mock_get_models
    main.get_shap_explainer = mock_get_shap_explainer

    body = {
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

    try:
        response = client.post(
            "/predict",
            json=body,
        )

        assert response.status_code == 200

        data = response.json()

        assert data["churn_prediction"] == 1
        assert data["churn_probability"] == 0.6928
        assert data["segment"] == 1
        assert data["segment_name"] == "New At-Risk"

        factors = data["top_factors"]

        assert factors

        features = [
            factor["feature"]
            for factor in factors
        ]

        assert "tenure" in features
        assert "TotalCharges" in features

        assert (
            "InternetService = Fiber optic"
            in features
        )

        assert (
            "Contract = Month-to-month"
            in features
        )

        assert (
            "Contract = Two year"
            not in features
        )

    finally:
        main.get_models = original_get_models
        main.get_shap_explainer = original_get_shap_explainer

        get_models.cache_clear()
        get_shap_explainer.cache_clear()