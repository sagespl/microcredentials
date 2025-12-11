"""
This is a boilerplate pipeline 'nn_model_training'
generated using Kedro 0.19.13
"""

from functools import update_wrapper, partial

from kedro.pipeline import node, Pipeline, pipeline  # noqa

from common.collators import collate_fn
from ml_pipelines.pipelines.nn_model_training.nodes import (
    build_model,
    build_image_transformer,
    build_dataloader,
    train,
    build_criterion,
    evaluate_on_test,
    save_model,
)


def create_nn_model_training_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                name="build_model_node",
                inputs=["params:model", "init_model_state"],
                outputs="model",
                func=build_model,
            ),
            node(
                name="build_train_image_to_tensor_transformer_node",
                inputs=["params:train.transformer", "params:seed"],
                outputs="train_image_to_tensor_transformer",
                func=build_image_transformer,
            ),
            node(
                name="build_evaluate_image_to_tensor_transformer_node",
                inputs=["params:eval.transformer", "params:seed"],
                outputs="evaluate_image_to_tensor_transformer",
                func=build_image_transformer,
            ),
            node(
                name="build_train_dataloader_node",
                inputs=[
                    "nn_data_train",
                    "train_image_to_tensor_transformer",
                    "params:batch_size",
                ],
                outputs="train_data_loader",
                func=update_wrapper(
                    partial(build_dataloader, shuffle=True, collate_fn=collate_fn),
                    build_dataloader,
                ),
            ),
            node(
                name="build_val_dataloader_node",
                inputs=[
                    "nn_data_val",
                    "evaluate_image_to_tensor_transformer",
                    "params:batch_size",
                ],
                outputs="val_data_loader",
                func=update_wrapper(
                    partial(build_dataloader, collate_fn=collate_fn), build_dataloader
                ),
            ),
            node(
                name="build_test_dataloader_node",
                inputs=[
                    "nn_data_test",
                    "evaluate_image_to_tensor_transformer",
                    "params:batch_size",
                ],
                outputs="test_data_loader",
                func=update_wrapper(
                    partial(build_dataloader, collate_fn=collate_fn), build_dataloader
                ),
            ),
            node(
                name="build_criterion_node",
                inputs=None,
                outputs="criterion",
                func=build_criterion,
            ),
            node(
                name="train_model_node",
                inputs=[
                    "model",
                    "train_data_loader",
                    "val_data_loader",
                    "criterion",
                    "params:train.hyperparameters",
                ],
                outputs="best_model",
                func=train,
            ),
            node(
                name="evaluate_model_node",
                inputs=["best_model", "test_data_loader", "criterion"],
                outputs=None,
                func=evaluate_on_test,
            ),
            node(
                name="save_trained_model_node",
                inputs=["best_model", "params:model"],
                outputs=["trained_model_state", "trained_model"],
                func=save_model,
            ),
        ]
    )
