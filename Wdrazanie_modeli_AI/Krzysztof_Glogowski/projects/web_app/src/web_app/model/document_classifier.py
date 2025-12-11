import io
import logging

import fsspec
import torch
from torch.jit import ScriptModule

from web_app.utils.device import get_device


class DocumentClassifier:
    def __init__(self, model: ScriptModule):
        self.model = model
        self.model.eval()

    @classmethod
    def from_path(cls, path: str) -> "DocumentClassifier":
        logging.info("Creating DocumentClusteringModel from model state path.")
        with fsspec.open(path) as f:
            buffer = io.BytesIO(f.read())
        model = torch.jit.load(buffer).to(get_device())
        return cls(model)

    def classify(self, document_as_images: torch.Tensor, lengths: torch.Tensor) -> dict[str, int]:
        with torch.no_grad():
            output: torch.Tensor = self.model(document_as_images, lengths)
        return {"label": int(output.argmax().item())}

    def classify_proba(self, document_as_images: torch.Tensor, lengths: torch.Tensor):
        with torch.no_grad():
            predicted_proba = self.model.predict_proba(document_as_images, lengths)
        labels_sorted_by_proba = torch.argsort(predicted_proba, descending=True)
        classification_result = [
            {"label": int(label), "confidence": float(predicted_proba[label])}
            for label in labels_sorted_by_proba
        ]
        return classification_result
