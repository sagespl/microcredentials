"""
This is a boilerplate pipeline 'data_preprocessing'
generated using Kedro 0.19.13
"""
from io import BytesIO
from pathlib import Path

import pandas as pd
from PIL import Image
from fsspec import AbstractFileSystem
from pymupdf import Page, pymupdf
from sklearn.model_selection import train_test_split

from common.input_file_validator import InputFileValidator
from ml_pipelines.file_system_utils import get_filesystem
from ml_pipelines.logger import logger


def convert_pdf_jpgs(
    dataset: pd.DataFrame,
    output_dir: str,
    fs_args: dict,
    credentials: dict,
) -> pd.DataFrame:
    _fs: AbstractFileSystem = get_filesystem(output_dir, fs_args, credentials)

    output: dict = {}
    validator = InputFileValidator()

    for row in dataset.itertuples(index=False):
        jpgs_dir_name = __convert_pdf_name_to_dir_name(row.path)
        image_paths = []

        with _fs.open(row.path, "rb") as f:
            errors = validator.validate(f)
            if len(errors) == 0:
                file = f.read()

        if len(errors) == 0:
            with pymupdf.open(stream=file, filetype="pdf") as pdf:
                for i in range(len(pdf)):
                    page = pdf.load_page(i)
                    img_buffer = __convert_pdf_page_to_img_buffer(page)
                    image_path = f"{output_dir}/{jpgs_dir_name}/{jpgs_dir_name}_{i}.jpg"
                    image_paths.append(image_path)

                    with _fs.open(image_path, "wb") as f:
                        f.write(img_buffer.getvalue())

            output.setdefault("paths", []).append(image_paths)
            output.setdefault("label", []).append(row.label)
        else:
            logger.warning(
                f"File validation failed for {row.path}: {errors}. File not included into final dataset."
            )

    return pd.DataFrame(output)


def split_dataset(
    all_data: pd.DataFrame, dataset_sizes: dict, seed: int
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train_full, test = train_test_split(
        all_data, test_size=dataset_sizes["test"], random_state=seed
    )
    train, val = train_test_split(train_full, test_size=dataset_sizes["val"], random_state=seed)

    return train, val, test


def __convert_pdf_name_to_dir_name(pdf_path: str) -> str:
    pdf_stem = Path(pdf_path).stem
    return pdf_stem.replace(" ", "_").lower()


def __convert_pdf_page_to_img_buffer(page: Page) -> BytesIO:
    pix = page.get_pixmap()
    image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    img_buffer = BytesIO()
    image.save(img_buffer, format="JPEG")
    img_buffer.seek(0)
    return img_buffer
