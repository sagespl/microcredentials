"""
This is a boilerplate pipeline 'nn_model_inference'
generated using Kedro 0.19.13
"""

import time

import numpy as np
import timm
import torch
from fsspec import AbstractFileSystem
from torch.nn.functional import softmax

from common.converters import pdf_to_model_input
from common.input_file_validator import InputFileValidator
from ml_pipelines.models import (
    ModelState,
    DocumentClassifier,
    AvgImageEncoder,
    RecursiveImageEncoder,
    MLP,
)
from common.torch_utils import get_device
from ml_pipelines.file_system_utils import get_filesystem
from ml_pipelines.logger import logger


def download_file(filepath: str, fs_args: dict, credentials: dict) -> str:
    local_path = f"projects/ml_pipelines/data/01_raw/inference/{int(time.time() * 1000)}.pdf"
    _fs: AbstractFileSystem = get_filesystem(filepath, fs_args, credentials)

    with _fs.open(filepath, mode="rb", credentials=credentials, fs_args=fs_args) as remote_file:
        with open(local_path, "wb") as local_file:
            local_file.write(remote_file.read())

    return local_path


def validate_file(filepath: str) -> str:
    with open(filepath, mode="rb") as file:
        validator = InputFileValidator()
        errors = validator.validate(file)
    if errors:
        raise ValueError(f"File validation failed: {errors}")
    return filepath


def convert_pdf_to_model_input(
    filepath: str, transformer_config: dict | None = None
) -> tuple[torch.Tensor, torch.Tensor]:
    return pdf_to_model_input(filepath, transformer_config)


def build_model(model_state_dict: dict) -> torch.nn.Module:
    model_state = ModelState.from_dict(model_state_dict)
    encoder = _build_encoder(model_state)
    classification_head = _build_classification_head(model_state)
    model = DocumentClassifier(encoder=encoder, classification_head=classification_head)
    model.to(get_device())
    return model


def _build_encoder(model_state: ModelState) -> AvgImageEncoder | RecursiveImageEncoder:
    backbone = timm.create_model(model_state.encoder_backbone, pretrained=True, num_classes=0)
    if model_state.encoder_type.lower() == "avg":
        return AvgImageEncoder(backbone)
    elif model_state.encoder_type.lower() == "rnn":
        return RecursiveImageEncoder(
            backbone=backbone,
            hidden_size=model_state.encoder_rnn_hidden_size,
            num_layers=model_state.encoder_rnn_num_layers,
            dropout=model_state.encoder_rnn_dropout,
        )
    else:
        raise ValueError(f"Unknown encoder type: {model_state.encoder_type}")


def _build_classification_head(model_state: ModelState) -> MLP:
    return MLP(
        input_size=model_state.classification_head_input_size,
        hidden_shape=model_state.classification_head_hidden_shape,
        output_size=model_state.classification_head_output_size,
        dropout=model_state.classification_head_dropout,
    )


def predict(model: torch.nn.Module, model_input: tuple[torch.Tensor, torch.Tensor]) -> torch.Tensor:
    model.eval()
    with torch.no_grad():
        predictions = model(*model_input)
        predictions_proba = softmax(predictions, dim=1)
    return predictions_proba.squeeze(0)


def log_prediction_results(predicted_proba: torch.Tensor) -> None:
    predicted_proba_array = predicted_proba.cpu().numpy()
    labels_sorted_by_proba = np.argsort(-predicted_proba_array)
    prediction_report = {label: predicted_proba_array[label] for label in labels_sorted_by_proba}

    for label, proba in prediction_report.items():
        logger.info(f"Label: {label}, Probability: {proba:.4f}")
