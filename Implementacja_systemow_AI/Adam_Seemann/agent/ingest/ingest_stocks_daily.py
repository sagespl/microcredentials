import logging
from collections.abc import Iterable
from pathlib import Path

from data.db import connect_db

logger = logging.getLogger(__name__)

REQUIRED_MIN_COLUMNS = ["isin", "date"]


def _fold_polish(s: str) -> str:
    if s is None:
        return s
    s = s.strip().lower()
    replacements = {
        "ą": "a",
        "ć": "c",
        "ę": "e",
        "ł": "l",
        "ń": "n",
        "ó": "o",
        "ś": "s",
        "ż": "z",
        "ź": "z",
    }
    for a, b in replacements.items():
        s = s.replace(a, b)
    return s


def validate_columns(columns: Iterable[str]) -> None:
    # build normalized set: apply folding and header mapping to detect required logical names
    header_map = {
        "data": "date",
        "nazwa": "name",
        "isin": "isin",
        "waluta": "currency",
        "kurs otwarcia": "open",
        "kurs max": "high",
        "kurs min": "low",
        "kurs zamkniecia": "close",
        "zmiana": "change_pct",
        "wolumen": "volume",
        "liczba transakcji": "num_trades",
        "obrot": "turnover",
    }

    normalized = set()
    for col in columns:
        fk = _fold_polish(col)
        normalized.add(header_map.get(fk, fk))

    missing = [c for c in REQUIRED_MIN_COLUMNS if c not in normalized]
    if missing:
        raise ValueError(f"Missing required columns for stocks_daily: {missing}")


def ingest_stocks_daily(df, source: Path) -> int:
    validate_columns(df.columns)
    rows = []
    # mapping of common Polish headers to normalized field names
    header_map = {
        "data": "date",
        "nazwa": "name",
        "isin": "isin",
        "waluta": "currency",
        "kurs otwarcia": "open",
        "kurs max": "high",
        "kurs min": "low",
        "kurs zamkniecia": "close",
        "zmiana": "change_pct",
        "wolumen": "volume",
        "liczba transakcji": "num_trades",
        "obrot": "turnover",
    }

    def normalize_row(raw_row: dict) -> dict:
        out = {}
        for k, v in raw_row.items():
            if k is None:
                continue
            fk = _fold_polish(k)
            mapped = header_map.get(fk, fk)
            out[mapped] = v
        return out

    for raw_row in df.to_dict(orient="records"):
        row = normalize_row(raw_row)
        rows.append(
            (
                row.get("name"),
                row.get("ticker"),
                row.get("isin"),
                row.get("date"),
                row.get("open"),
                row.get("high"),
                row.get("low"),
                row.get("close"),
                row.get("volume"),
                row.get("num_trades"),
                row.get("change_pct"),
                row.get("turnover"),
                row.get("currency"),
            )
        )

    if not rows:
        raise ValueError("No rows found in stocks_daily file")

    logger.info("Ingesting %d rows from %s", len(rows), source.name)
    with connect_db() as conn:
        cursor = conn.cursor()
        for (
            name,
            ticker,
            isin,
            date,
            open_v,
            high_v,
            low_v,
            close_v,
            volume,
            num_trades,
            change_pct,
            turnover,
            currency,
        ) in rows:
            # check if exists
            cursor.execute(
                "SELECT id FROM stocks_daily WHERE isin = ? AND date = ?",
                (isin, date),
            )
            existing = cursor.fetchone()
            if existing:
                cursor.execute(
                    """
                    UPDATE stocks_daily SET
                        name = ?, ticker = ?, open = ?, high = ?, low = ?, close = ?, volume = ?, num_trades = ?, change_pct = ?, turnover = ?, currency = ?
                    WHERE id = ?
                    """,
                    (
                        name,
                        ticker,
                        open_v,
                        high_v,
                        low_v,
                        close_v,
                        volume,
                        num_trades,
                        change_pct,
                        turnover,
                        currency,
                        existing["id"],
                    ),
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO stocks_daily
                        (name, ticker, isin, date, open, high, low, close, volume, num_trades, change_pct, turnover, currency)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        name,
                        ticker,
                        isin,
                        date,
                        open_v,
                        high_v,
                        low_v,
                        close_v,
                        volume,
                        num_trades,
                        change_pct,
                        turnover,
                        currency,
                    ),
                )
        conn.commit()
    return len(rows)
