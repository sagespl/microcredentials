import logging
from pathlib import Path

import pandas as pd

from data.db import insert_ticker

logger = logging.getLogger(__name__)

COLMAP = {
    "ticker": "ticker",
    "name": "name",
    "sector": "sector",
    "market": "market",
}

REQUIRED = {"ticker", "name"}


def ingest_ticker_map(df: pd.DataFrame, path: Path) -> int:
    """Ingest a TICKER_MAP file into SQLite (tickers table). Returns number of rows processed."""
    df = df.rename(columns=lambda c: COLMAP.get(str(c).strip().lower(), str(c).strip().lower()))

    missing = REQUIRED - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns for ticker_map: {missing}")

    count = 0
    for _, row in df.iterrows():
        ticker = row.get("ticker")
        if pd.isna(ticker) or not str(ticker).strip():
            continue
        insert_ticker(
            ticker=str(ticker).strip(),
            name=row.get("name"),
            sector=row.get("sector") if "sector" in df.columns else None,
            market=row.get("market") if "market" in df.columns else None,
        )
        count += 1

    logger.info("Ingested %d TICKER_MAP rows from %s", count, path.name)
    return count
