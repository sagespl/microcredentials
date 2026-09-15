"""Seed the local SQLite database with deterministic sample stock quotes."""

from __future__ import annotations

import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from data.db import connect_db, initialize_database  # noqa: E402


def seed_sample_data(
    path: Path | str | None = None,
    ticker: str = "AGPW",
    isin: str = "PLAGPW000001",
    rows: int = 40,
) -> int:
    """Insert reproducible daily quotes and return the number of rows written."""
    if rows <= 0:
        raise ValueError("rows must be positive")

    database_path = initialize_database(path) if path is not None else initialize_database()
    start_date = date(2026, 1, 2)
    quotes = []
    for offset in range(rows):
        close = 100.0 + offset * 0.5
        quotes.append(
            (
                ticker,
                "AGPW Sample S.A.",
                isin,
                (start_date + timedelta(days=offset)).isoformat(),
                close - 1,
                close + 2,
                close - 2,
                close,
                1000 + offset * 25,
                10 + offset,
                0.5,
                (1000 + offset * 25) * close,
                "PLN",
            )
        )

    with connect_db(database_path) as connection:
        connection.executemany(
            """
            INSERT INTO stocks_daily (
                ticker, name, isin, date, open, high, low, close, volume,
                num_trades, change_pct, turnover, currency
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(isin, date) DO UPDATE SET
                ticker = excluded.ticker,
                name = excluded.name,
                open = excluded.open,
                high = excluded.high,
                low = excluded.low,
                close = excluded.close,
                volume = excluded.volume,
                num_trades = excluded.num_trades,
                change_pct = excluded.change_pct,
                turnover = excluded.turnover,
                currency = excluded.currency
            """,
            quotes,
        )
    return len(quotes)


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed AGPW SQLite database with sample stock data.")
    parser.add_argument("--db", type=Path, default=None, help="Optional SQLite database path")
    parser.add_argument("--ticker", default="AGPW", help="Ticker to seed")
    parser.add_argument("--isin", default="PLAGPW000001", help="ISIN to seed")
    parser.add_argument("--rows", type=int, default=40, help="Number of daily rows")
    args = parser.parse_args()

    count = seed_sample_data(args.db, args.ticker, args.isin, args.rows)
    print(f"Seeded {count} rows for {args.ticker}.")


if __name__ == "__main__":
    main()
