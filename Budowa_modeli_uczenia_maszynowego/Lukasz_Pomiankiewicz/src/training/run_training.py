from __future__ import annotations

from sklearn.model_selection import train_test_split

from src.data.load_data import load_data
from src.evaluation.evaluate import evaluate_model
from src.features.preprocessing import preprocess_data
from src.models.save_model import save_model
from src.training.train import train_model


def run_training(
    model_name: str = "logistic_regression",
):
    """
    Execute full training workflow.
    """

    # Load data
    df = load_data()

    # Cleaning
    df = preprocess_data(df)

    # Split features and target
    X = df.drop(
        columns=["Churn"]
    )

    y = df["Churn"].map(
        {
            "No": 0,
            "Yes": 1,
        }
    )

    # Feature groups
    numeric_features = [
        "SeniorCitizen",
        "tenure",
        "MonthlyCharges",
        "TotalCharges",
    ]

    categorical_features = [
        col
        for col in X.columns
        if col not in numeric_features
    ]

    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    # Train
    model = train_model(
        X_train=X_train,
        y_train=y_train,
        model_name=model_name,
        numeric_features=numeric_features,
        categorical_features=categorical_features,
    )

    # Evaluate
    metrics = evaluate_model(
        model=model,
        X_test=X_test,
        y_test=y_test,
    )

    save_model(model)

    return model, metrics