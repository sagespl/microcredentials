from typing import Literal

import torch
from torchmetrics import Accuracy
from torchmetrics.classification import (
    MulticlassPrecision,
    MulticlassRecall,
    MulticlassF1Score,
)


class ClassificationReport:
    def __init__(
        self,
        device: torch.device,
        num_classes: int = 4,
        average: Literal["micro", "macro", "weighted", "none"] | None = "macro",
    ):
        task: Literal["binary", "multiclass", "multilabel"] = (
            "multiclass" if num_classes > 2 else "binary"
        )
        self.accuracy = Accuracy(task=task, num_classes=num_classes).to(device)
        self.precision = MulticlassPrecision(num_classes=num_classes, average=average).to(device)
        self.recall = MulticlassRecall(num_classes=num_classes, average=average).to(device)
        self.f1 = MulticlassF1Score(num_classes=num_classes, average=average).to(device)

    def generate(self, y_pred, y_true) -> tuple[float, float, float, float]:
        accuracy_score = self.accuracy(y_pred, y_true)
        precision_score = self.precision(y_pred, y_true)
        recall_score = self.recall(y_pred, y_true)
        f1_score = self.f1(y_pred, y_true)

        return (
            accuracy_score.item(),
            precision_score.item(),
            recall_score.item(),
            f1_score.item(),
        )
