"""
This is a boilerplate pipeline 'nn_model_inference'
generated using Kedro 0.19.13
"""

from kedro.pipeline import node, Pipeline, pipeline  # noqa

from ml_pipelines.pipelines.nn_model_inference.nodes import (
    download_file,
    convert_pdf_to_model_input,
    build_model,
    predict,
    log_prediction_results,
    validate_file,
)


def create_nn_model_inference_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                name="download_pdf_node",
                inputs=["params:filepath", "params:fs_args", "params:credentials"],
                outputs="local_path",
                func=download_file,
            ),
            node(
                name="validate_pdf_node",
                inputs=["local_path"],
                outputs="validated_local_path",
                func=validate_file,
            ),
            node(
                name="convert_pdf_to_model_input_node",
                inputs=["validated_local_path"],
                outputs="model_input",
                func=convert_pdf_to_model_input,
            ),
            node(
                name="build_model_node",
                inputs=["trained_model_state"],
                outputs="model",
                func=build_model,
            ),
            node(
                name="predict_node",
                inputs=["model", "model_input"],
                outputs="prediction",
                func=predict,
            ),
            node(
                name="log_prediction_node",
                inputs=["prediction"],
                outputs=None,
                func=log_prediction_results,
            ),
        ]
    )
