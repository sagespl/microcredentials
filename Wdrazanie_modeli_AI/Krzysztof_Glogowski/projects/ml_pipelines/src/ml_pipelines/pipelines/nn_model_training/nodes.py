"""
This is a boilerplate pipeline 'nn_model_training'
generated using Kedro 0.19.13
"""

from dataclasses import asdict
from typing import Any, Callable, Literal

import flatdict
import mlflow
import timm
import torch
from PIL import Image
from torch import nn, optim
from torch.utils.data import DataLoader
from tqdm import tqdm

from datasets import ImageSequencesDataset
from ml_pipelines.classification_report import ClassificationReport
from ml_pipelines.early_stopper import EarlyStopper, StopMetric
from common.image_transformers import transform
from ml_pipelines.models import (
    AvgImageEncoder,
    RecursiveImageEncoder,
    DocumentClassifier,
    MLP,
    ModelState,
)
from common.torch_utils import get_device, freez_model, get_model_device
from ml_pipelines.logger import logger


def build_model(
    config: dict[str, Any],
    init_model_state_dict: dict | None,
) -> DocumentClassifier:
    encoder = _build_encoder(config["encoder"])
    classification_head = MLP(input_size=encoder.output_size, **config["classification_head"])
    model = DocumentClassifier(encoder=encoder, classification_head=classification_head)
    _load_init_model_state(model, init_model_state_dict, config)

    return model


def _load_init_model_state(
    model: DocumentClassifier,
    init_model_state_dict: dict | None,
    config: dict[str, Any],
):
    if init_model_state_dict is None:
        logger.info("No init_model_state provided, skipping loading of initial model state.")
        return

    flat_config = flatdict.FlatDict(config, delimiter="_")
    equal_configs = True
    for key in flat_config.keys():
        if key not in init_model_state_dict or init_model_state_dict[key] != flat_config[key]:
            equal_configs = False
            break

    if equal_configs:
        model.load_state_dict(init_model_state_dict["model_state_dict"])
        logger.info("Model state loaded from init_model_state.")

    else:
        logger.warning(
            "Model state not loaded from init_model_state, because configs are not equal. "
            "Please check the model configuration and init_model_state."
        )


def _build_encoder(config: dict[str, Any]) -> AvgImageEncoder | RecursiveImageEncoder:
    backbone = timm.create_model(config["backbone"], pretrained=True, num_classes=0)
    encoder: AvgImageEncoder | RecursiveImageEncoder
    if config["type"].lower() == "avg":
        encoder = AvgImageEncoder(backbone)
    else:
        encoder = RecursiveImageEncoder(backbone, **config["rnn"])
    return encoder


def build_image_transformer(
    config: dict[str, Any], seed: int
) -> Callable[[Image.Image], torch.Tensor]:
    return transform(config, seed)


def build_dataloader(
    dataset: ImageSequencesDataset,
    image_transformer: Callable[[Image.Image], torch.Tensor],
    batch_size: int,
    collate_fn: Callable[[list], Any],
    shuffle: bool = False,
) -> DataLoader:
    dataloader = DataLoader(
        dataset.with_transform(image_transformer),
        batch_size=batch_size,
        shuffle=shuffle,
        collate_fn=collate_fn,
    )
    return dataloader


def build_criterion() -> nn.Module:
    return nn.CrossEntropyLoss()


def train(
    model: DocumentClassifier,
    train_dataloader: DataLoader,
    valid_dataloader: DataLoader,
    criterion: nn.Module,
    config: dict[str, Any],
) -> DocumentClassifier:
    model.to(get_device())
    freez_model(model.encoder.backbone)
    classification_report = ClassificationReport(get_model_device(model))
    early_stopper = EarlyStopper(**config["early_stopper"])
    stop_metric = StopMetric[config["stop_metric"]]
    optimizer = optim.Adam(model.parameters(), **config["optimizer"])
    for epoch in tqdm(range(config["epochs"])):
        metrics_train = _train_one_epoch(
            model, train_dataloader, optimizer, criterion, classification_report
        )
        metrics_valid = _evaluate(model, valid_dataloader, criterion, classification_report)
        logger.info(f"Epoch {epoch + 1}:")
        _log_metrics("train", *metrics_train, epoch)
        _log_metrics("val", *metrics_valid, epoch)

        if early_stopper.early_stop(metrics_valid[stop_metric.value], model):
            logger.info(
                f"Early stopping on epoch {epoch + 1}, {stop_metric.name}: {metrics_valid[stop_metric.value]}"
            )
            break
    if early_stopper.best_model_state_dict is not None:
        model.load_state_dict(early_stopper.best_model_state_dict)

    return model


def _train_one_epoch(
    model: DocumentClassifier,
    train_dataloader: DataLoader,
    optimizer: optim.Optimizer,
    criterion: nn.Module,
    classification_report: ClassificationReport,
):
    model.train()
    model_device = get_model_device(model)
    epoch_loss = 0
    y_true = torch.empty(0).to(model_device)
    y_pred = torch.empty(0).to(model_device)
    optimizer.zero_grad()

    for items, lengths, labels in tqdm(train_dataloader):
        items, lengths, labels = (
            items.to(model_device),
            lengths.to(model_device),
            labels.to(model_device),
        )
        output = model(items, lengths)
        _, labels_pred = output.max(dim=1)

        y_true = torch.cat((y_true, labels), dim=0)
        y_pred = torch.cat((y_pred, labels_pred), dim=0)

        loss = criterion(output, labels)
        loss.backward()
        optimizer.step()
        epoch_loss += loss.item() * items.size(0)
    avg_epoch_loss = epoch_loss / len(train_dataloader.dataset)
    accuracy, precision, recall, f1 = classification_report.generate(y_pred, y_true)
    return avg_epoch_loss, accuracy, precision, recall, f1


def evaluate_on_test(model: DocumentClassifier, dataloader: DataLoader, criterion: nn.Module):
    classification_report = ClassificationReport(get_model_device(model))
    metrics = _evaluate(model, dataloader, criterion, classification_report)
    _log_metrics("test", *metrics)


def _evaluate(
    model: DocumentClassifier,
    dataloader: DataLoader,
    criterion: nn.Module,
    classification_report: ClassificationReport,
):
    model.eval()
    freez_model(model.encoder.backbone)
    model_device = get_model_device(model)
    with torch.no_grad():
        epoch_loss = 0
        y_true = torch.empty(0).to(model_device)
        y_pred = torch.empty(0).to(model_device)

        for items, lengths, labels in tqdm(dataloader):
            items, lengths, labels = (
                items.to(model_device),
                lengths.to(model_device),
                labels.to(model_device),
            )
            output = model(items, lengths)
            _, labels_pred = output.max(dim=1)

            y_true = torch.cat((y_true, labels), dim=0)
            y_pred = torch.cat((y_pred, labels_pred), dim=0)

            loss = criterion(output, labels)
            epoch_loss += loss.item() * items.size(0)
    avg_epoch_loss = epoch_loss / len(dataloader.dataset)
    accuracy, precision, recall, f1 = classification_report.generate(y_pred, y_true)
    return avg_epoch_loss, accuracy, precision, recall, f1


def _log_metrics(
    stage: Literal["train", "val", "test"],
    loss: float,
    accuracy: float,
    precision: float,
    recall: float,
    f1: float,
    epoch: int | None = None,
):
    logger.info(
        f"{stage}_loss={loss}, {stage}_accuracy={accuracy}, {stage}_precision={precision}, {stage}_recall={recall}, {stage}_f1={f1}"
    )
    mlflow.log_metric(f"{stage}_loss", loss, step=epoch)
    mlflow.log_metric(f"{stage}_accuracy", accuracy, step=epoch)
    mlflow.log_metric(f"{stage}_precision", precision, step=epoch)
    mlflow.log_metric(f"{stage}_recall", recall, step=epoch)
    mlflow.log_metric(f"{stage}_f1", f1, step=epoch)


def save_model(model: DocumentClassifier, config: dict[str, Any]):
    model.cpu()
    model_state = ModelState(
        model_state_dict=model.state_dict(),
        classification_head_input_size=model.classification_head.input_size,
        **flatdict.FlatDict(config, delimiter="_"),
    )
    model_state_dict = asdict(model_state)
    mlflow.log_dict(model_state_dict, "model_state.json")

    return model_state_dict, model
