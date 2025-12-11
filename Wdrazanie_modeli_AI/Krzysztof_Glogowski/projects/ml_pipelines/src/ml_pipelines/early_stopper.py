from copy import deepcopy
from enum import Enum

from torch import nn


class EarlyStopper:
    def __init__(self, patience: int = 1, min_delta: float = 0):
        self.patience = patience
        self.min_delta = min_delta
        self.counter = 0
        self.min_stop_metric_value = float("inf")
        self.best_model_state_dict: dict | None = None

    def early_stop(self, metric_value: float, model: nn.Module) -> bool:
        if metric_value < self.min_stop_metric_value:
            self.min_stop_metric_value = metric_value
            self.counter = 0
            self.best_model_state_dict = deepcopy(model.state_dict())
        elif metric_value > (self.min_stop_metric_value + self.min_delta):
            self.counter += 1
            if self.counter >= self.patience:
                return True
        return False


class StopMetric(Enum):
    LOSS = 0
    ACCURACY = 1
    PRECISION = 2
    RECALL = 3
    F1 = 4
