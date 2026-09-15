import logging
from pathlib import Path

import pandas as pd

from data.db import insert_sector_company

logger = logging.getLogger(__name__)

COLMAP = {
    "sector": "sector",
    "ticker": "ticker",
    "company_name": "company_name",
    "name": "company_name",
}

REQUIRED = {"sector", "ticker"}


def ingest_sector_composition(df: pd.DataFrame, path: Path) -> int:
    """Ingest a SECTOR_COMPOSITION file into SQLite (sector_companies table)."""
    df = df.rename(columns=lambda c: COLMAP.get(str(c).strip().lower(), str(c).strip().lower()))

    missing = REQUIRED - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns for sector_composition: {missing}")

    count = 0
    for _, row in df.iterrows():
        sector = row.get("sector")
        ticker = row.get("ticker")
        if pd.isna(sector) or pd.isna(ticker) or not str(sector).strip() or not str(ticker).strip():
            continue
        insert_sector_company(
            sector=str(sector).strip(),
            ticker=str(ticker).strip(),
            company_name=row.get("company_name") if "company_name" in df.columns else None,
        )
        count += 1

    logger.info("Ingested %d SECTOR_COMPOSITION rows from %s", count, path.name)
    return count
