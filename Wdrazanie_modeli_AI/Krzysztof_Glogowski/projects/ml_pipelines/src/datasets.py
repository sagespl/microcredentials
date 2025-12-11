import ast
import io
from typing import Any, Callable

import albumentations as A
import numpy as np
import pandas as pd
import torch
from fsspec import AbstractFileSystem
from kedro.io import AbstractDataset, DatasetError
from kedro_datasets.pickle import PickleDataset
from PIL import Image
from torch import nn, ScriptModule
from torch.utils.data import Dataset

from ml_pipelines.file_system_utils import get_filesystem


class ImageSequencesDataset(Dataset, AbstractDataset[pd.DataFrame, "ImageSequencesDataset"]):
    def __init__(
        self,
        filepath: str,
        paths_column: str = "paths",
        label_column: str | None = None,
        fs_args: dict | None = None,
        credentials: dict | None = None,
        transform: Callable[[Image.Image], torch.Tensor] | None = None,
    ):
        super().__init__()
        self.data_file_path = filepath
        self.paths_column = paths_column
        self.label_column = label_column
        self.data: pd.DataFrame | None = None
        self.transform_fn = transform
        self._fs: AbstractFileSystem = get_filesystem(self.data_file_path, fs_args, credentials)

    # Kedro Dataset methods
    def load(self) -> "ImageSequencesDataset":
        self.data = pd.read_csv(self.data_file_path)
        self.data[self.paths_column] = self.data[self.paths_column].apply(ast.literal_eval)
        return self

    def save(self, data: pd.DataFrame) -> None:
        self.data = data
        with self._fs.open(self.data_file_path, "wt", encodings="utf-8") as f:
            data.to_csv(f, index=False)

    def _describe(self) -> dict[str, Any]:
        return {
            "type": "ImageSequencesDataset",
            "data_file_path": str(self.data_file_path),
            "paths_column": self.paths_column,
            "label_column": self.label_column,
        }

    # PyTorch Dataset methods
    def __len__(self) -> int:
        return 0 if self.data is None else len(self.data)

    def __getitem__(self, idx: int) -> tuple[list[torch.Tensor], int] | list[torch.Tensor]:
        if self.data is None:
            raise DatasetError("Dataset is not loaded. Call load() first.")
        img_paths = self.data.loc[idx, self.paths_column]
        label = None if self.label_column is None else self.data.loc[idx, self.label_column]
        item_1 = []

        for img_path in img_paths:
            with self._fs.open(img_path, "rb") as f:
                img = Image.open(f)
                item_1.append(self._transform(img))

        if label is not None:
            return item_1, label
        else:
            return item_1

    # helpers
    def _transform(self, img: Image.Image) -> torch.Tensor:
        if self.transform_fn is not None:
            return self.transform_fn(img)
        return A.ToTensorV2()(image=np.array(img))["image"]

    def with_transform(
        self, transform: Callable[[Image.Image], torch.Tensor] | None
    ) -> "ImageSequencesDataset":
        self.transform_fn = transform
        return self


class OptionalPickleDataset(PickleDataset):
    def _load(self):
        try:
            return super().load()
        except (DatasetError, FileNotFoundError):
            return None


class PyTorchJitDataset(AbstractDataset[nn.Module, ScriptModule]):
    def __init__(
        self,
        filepath: str,
        fs_args: dict | None = None,
        credentials: dict | None = None,
        transform: Callable[[Image.Image], torch.Tensor] | None = None,
    ):
        super().__init__()
        self.model_path = filepath
        self.transform_fn = transform
        self._fs: AbstractFileSystem = get_filesystem(self.model_path, fs_args, credentials)

    def load(self) -> ScriptModule:
        with self._fs.open(self.model_path, "rb") as f:
            buffer = io.BytesIO(f.read())
        return torch.jit.load(buffer)

    def save(self, data: nn.Module) -> None:
        scripted_model = torch.jit.script(data)
        buffer = io.BytesIO()
        torch.jit.save(scripted_model, buffer)
        buffer.seek(0)
        with self._fs.open(self.model_path, "wb") as f:
            f.write(buffer.read())

    def _describe(self) -> dict[str, Any]:
        return {"type": "PyTorchJitDataset", "model_path": str(self.model_path)}
