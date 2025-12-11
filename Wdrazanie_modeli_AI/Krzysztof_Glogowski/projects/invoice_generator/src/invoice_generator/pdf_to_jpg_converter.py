import os
from pathlib import Path

import pandas as pd
import pymupdf
import typer
from tqdm import tqdm

app = typer.Typer()


@app.command()
def convert_pdf_to_jpgs(
    pdfs_dir: str = "invoice_generator/resources/pdf/generated",
    jpgs_dir: str = "invoice_generator/resources/jpg/generated",
    resolution: int | None = None,
):
    os.makedirs(jpgs_dir, exist_ok=True)
    pdfs_path = Path(pdfs_dir)
    jpgs_path = Path(jpgs_dir)
    pdfs_metadata = pd.read_csv(pdfs_path / "metadata.csv")
    jpgs_metadata_dict = {"paths": [], "label": []}

    for row in tqdm(pdfs_metadata.itertuples(index=False), total=len(pdfs_metadata)):
        pdf_file_path, label = Path(row.path), row.label
        pdf_name = pdf_file_path.stem
        os.makedirs(jpgs_path / pdf_name)
        pdf = pymupdf.open(pdf_file_path)

        jpgs_paths = []
        for i in range(len(pdf)):
            page = pdf.load_page(i)
            pix = page.get_pixmap(dpi=resolution)
            jpg_path = jpgs_path / pdf_name / f"{pdf_name}_{i}.jpg"
            pix.save(jpg_path)
            jpgs_paths.append(os.path.abspath(jpg_path))

        jpgs_metadata_dict.get("paths").append(jpgs_paths)
        jpgs_metadata_dict.get("label").append(label)

    jpgs_metadata = pd.DataFrame(jpgs_metadata_dict)
    jpgs_metadata.to_csv(jpgs_path / "metadata.csv", index=False)


if __name__ == "__main__":
    app()
