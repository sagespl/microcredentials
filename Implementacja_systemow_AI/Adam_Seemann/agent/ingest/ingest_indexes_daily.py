import logging
from pathlib import Path

import pandas as pd

from data.db import insert_index_daily

logger = logging.getLogger(__name__)

# Mapowanie polskich nazw GPW → standardowe nazwy
COLMAP = {
    "data": "date",
    "nazwa": "index_name",
    "kurs otwarcia": "open",
    "kurs max": "high",
    "kurs min": "low",
    "kurs zamknięcia": "close",
    "kurs zamkniecia": "close",
    "wolumen": "volume",
    "liczba transakcji": "transactions",
    "obrót": "turnover",
}

REQUIRED = {"date", "index_name", "open", "high", "low", "close"}


def ingest_indexes_daily(df: pd.DataFrame, path: Path) -> int:
    """
    Ingest GPW INDEX_DAILY file into SQLite.
    Returns number of inserted rows.
    """

    # --- Normalizacja nazw kolumn ---
    df = df.rename(columns=lambda c: COLMAP.get(str(c).lower(), str(c).lower()))

    # --- Walidacja wymaganych kolumn ---
    missing = REQUIRED - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns for indexes_daily: {missing}")

    # --- Wybór tylko wymaganych kolumn ---
    df = df[list(REQUIRED)]

    # --- Konwersje typów ---
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # --- Wstawianie do bazy ---
    count = 0
    for _, row in df.iterrows():
        insert_index_daily(
            index_name=row["index_name"],
            date=row["date"],
            open=row["open"],
            high=row["high"],
            low=row["low"],
            close=row["close"],
        )
        count += 1

    logger.info("Inserted %d INDEX_DAILY rows from %s", count, path.name)
    return count
