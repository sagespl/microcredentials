"""
This is a boilerplate pipeline 'data_preprocessing'
generated using Kedro 0.19.13
"""

from kedro.pipeline import node, Pipeline, pipeline  # noqa

from ml_pipelines.pipelines.data_preprocessing.nodes import (
    convert_pdf_jpgs,
    split_dataset,
)


def create_data_preprocessing_pipeline() -> Pipeline:
    return pipeline(
        [
            node(
                name="convert_train_pdfs_to_jpgs_node",
                inputs=[
                    "dpp_all_pdfs",
                    "params:jpgs_dir",
                    "params:fs_args",
                    "params:credentials",
                ],
                outputs="dpp_all_jpgs",
                func=convert_pdf_jpgs,
            ),
            node(
                name="split_dataset_node",
                inputs=["dpp_all_jpgs", "params:dataset_sizes", "params:seed"],
                outputs=[
                    "dpp_train",
                    "dpp_val",
                    "dpp_test",
                ],
                func=split_dataset,
            ),
        ]
    )
