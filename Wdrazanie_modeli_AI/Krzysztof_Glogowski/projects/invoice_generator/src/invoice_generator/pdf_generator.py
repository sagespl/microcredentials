import os
import random

import pandas as pd
import typer
from tqdm import tqdm

from invoice_generator.pdf_generator.invoice_generator_provider import (
    provide_pdf_generator,
)

app = typer.Typer()


@app.command()
def generate_invoices(n: int = 5, path: str = "invoice_generator/resources/pdf/generated") -> None:
    os.makedirs(path, exist_ok=True)
    metadata = {"path": [], "label": []}

    for i in tqdm(range(n)):
        random_choice = random.randint(0, 3)
        invoice_generator = provide_pdf_generator(random_choice)
        invoice_name = f"invoice_{i}_type_{random_choice}.pdf"
        invoice_path = os.path.abspath(os.path.join(path, invoice_name))
        __add_metadata(invoice_path, random_choice, metadata)
        invoice_generator(os.path.join(path, invoice_name))

    metadata_df = pd.DataFrame(metadata)
    metadata_df.to_csv(os.path.join(path, "metadata.csv"), index=False)


def __add_metadata(file_name: str, label: int, labels: dict[str, list[str | int]]) -> None:
    labels["path"].append(file_name)
    labels["label"].append(label)


if __name__ == "__main__":
    app()
