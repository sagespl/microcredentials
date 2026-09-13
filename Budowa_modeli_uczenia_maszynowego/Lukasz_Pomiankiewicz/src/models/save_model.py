from pathlib import Path

import joblib
from sklearn.pipeline import Pipeline

MODEL_DIR = Path("models")
MODEL_PATH = MODEL_DIR / "churn_model.pkl"


def save_model(
    model: Pipeline,
    path: Path = MODEL_PATH,
) -> Path:
    """
    Save trained ML pipeline.
    """

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(
        model,
        path,
    )

    return path