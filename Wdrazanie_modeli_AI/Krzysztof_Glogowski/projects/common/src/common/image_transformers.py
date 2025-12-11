from copy import deepcopy
from typing import Any, Callable

import albumentations as A
import numpy as np
import torch
from PIL import Image

default_transformation_config = {
    "image_size": {"height": 224, "width": 224},
    "normalization": {"mean": [0.5, 0.5, 0.5], "std": [0.5, 0.5, 0.5]},
    "gaussian_blur_proba": 0,
    "random_brightness_contrast_proba": 0,
    "to_gray_proba": 0,
}


def transform(
    config: dict[str, Any] | None, seed: int | None = None
) -> Callable[[Image.Image], torch.Tensor]:
    if config is not None:
        for key, value in default_transformation_config.items():
            config.setdefault(key, value)
    if config is None:
        config = deepcopy(default_transformation_config)

    base_transform = A.Compose(
        [
            A.Resize(**config["image_size"]),
            A.GaussianBlur(p=config.get("gaussian_blur_proba")),
            A.RandomBrightnessContrast(p=config.get("random_brightness_contrast_proba")),
            A.ToGray(p=config.get("to_gray_proba")),
            A.Normalize(
                mean=tuple(config["normalization"]["mean"]),
                std=tuple(config["normalization"]["std"]),
            ),
            A.ToTensorV2(),
        ],
        seed=seed,
    )

    return lambda img: base_transform(image=np.array(img))["image"]
