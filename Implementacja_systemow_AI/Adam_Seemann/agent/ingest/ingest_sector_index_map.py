import logging
from pathlib import Path

import pandas as pd

from data.db import insert_sector_index_map

logger = logging.getLogger(__name__)

COLMAP = {
    "sector": "sector",
    "index_name": "index_name",
}

REQUIRED = {"sector", "index_name"}


def ingest_sector_index_map(df: pd.DataFrame, path: Path) -> int:
    """Ingest a SECTOR_INDEX_MAP file into SQLite (sector_index_map table)."""
    df = df.rename(columns=lambda c: COLMAP.get(str(c).strip().lower(), str(c).strip().lower()))

    missing = REQUIRED - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns for sector_index_map: {missing}")

    count = 0
    for _, row in df.iterrows():
        sector = row.get("sector")
        index_name = row.get("index_name")
        if pd.isna(sector) or pd.isna(index_name) or not str(sector).strip() or not str(index_name).strip():
            continue
        insert_sector_index_map(
            sector=str(sector).strip(),
            index_name=str(index_name).strip(),
        )
        count += 1

    logger.info("Ingested %d SECTOR_INDEX_MAP rows from %s", count, path.name)
    return count
