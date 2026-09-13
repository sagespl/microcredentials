import json
from datetime import UTC, datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

EXPERIMENTS_PATH = (
    PROJECT_ROOT
    / "experiments"
    / "results.json"
)


def save_experiment(
    model_name: str,
    params: dict,
    metrics: dict,
):
    """
    Save ML experiment results.
    """

    experiment = {
        "timestamp": datetime.now(UTC).isoformat(),
        "model": model_name,
        "params": params,
        "metrics": metrics,
    }

    EXPERIMENTS_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if EXPERIMENTS_PATH.exists():
        experiments = json.loads(
            EXPERIMENTS_PATH.read_text()
        )
    else:
        experiments = []

    experiments.append(
        experiment
    )

    EXPERIMENTS_PATH.write_text(
        json.dumps(
            experiments,
            indent=4,
        )
    )


import pandas as pd


def load_experiments() -> pd.DataFrame:
    """
    Load experiments as DataFrame.
    """

    if not EXPERIMENTS_PATH.exists():
        return pd.DataFrame()

    experiments = json.loads(
        EXPERIMENTS_PATH.read_text()
    )

    rows = []

    for exp in experiments:
        row = {
            "model": exp["model"],
            **exp["metrics"],
            **{
                f"param_{k}": v
                for k, v in exp["params"].items()
            },
        }

        rows.append(row)

    return pd.DataFrame(rows)


