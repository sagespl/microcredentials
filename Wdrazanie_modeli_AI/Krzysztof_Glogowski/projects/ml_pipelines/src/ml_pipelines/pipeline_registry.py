"""Project pipelines."""

from kedro.pipeline import Pipeline

from ml_pipelines.pipelines.data_preprocessing.pipeline import (
    create_data_preprocessing_pipeline,
)
from ml_pipelines.pipelines.nn_model_inference import create_nn_model_inference_pipeline
from ml_pipelines.pipelines.nn_model_training import create_nn_model_training_pipeline


def register_pipelines() -> dict[str, Pipeline]:
    """Register the project's pipelines.

    Returns:
        A mapping from pipeline names to ``Pipeline`` objects.
    """
    pipelines: dict[str, Pipeline] = {}
    # https://github.com/kedro-org/kedro/issues/2526
    pipelines["__default__"] = create_nn_model_training_pipeline()
    pipelines["data_preprocessing"] = create_data_preprocessing_pipeline()
    pipelines["nn_model_training"] = create_nn_model_training_pipeline()
    pipelines["nn_model_inference"] = create_nn_model_inference_pipeline()
    return pipelines
