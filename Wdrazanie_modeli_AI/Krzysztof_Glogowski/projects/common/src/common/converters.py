import os

import pymupdf
import torch
from PIL import Image

from common.collators import predict_collate_fn
from common.image_transformers import transform
from common.torch_utils import get_device


def pdf_to_model_input(
    filepath: str, transformer_config: dict | None = None
) -> tuple[torch.Tensor, torch.Tensor]:
    images = []
    with pymupdf.open(filepath) as pdf:
        for i in range(len(pdf)):
            page = pdf.load_page(i)
            pix = page.get_pixmap()
            image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            images.append(transform(transformer_config)(image).to(get_device()))

    os.remove(filepath)

    return predict_collate_fn([images])
