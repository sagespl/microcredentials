import tempfile

import torch

from common.converters import pdf_to_model_input


def to_model_input(document: bytes) -> tuple[torch.Tensor, torch.Tensor]:
    with tempfile.NamedTemporaryFile(mode="w+b", suffix=".pdf", delete=False) as tmp:
        tmp.write(document)
    model_input = pdf_to_model_input(tmp.name)
    return model_input
