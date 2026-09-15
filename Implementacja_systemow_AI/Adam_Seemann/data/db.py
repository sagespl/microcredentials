import sqlite3
from pathlib import Path

from data.migrator import run_migrations

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "agpw.db"
MIGRATIONS_DIR = BASE_DIR / "migrations"


def connect_db(
    path: Path | str | None = None,
    timeout: float = 30.0,
    check_same_thread: bool = True,
) -> sqlite3.Connection:
    """Open a SQLite database connection with foreign key support enabled.

    If `path` is None, use the module-level `DB_PATH` so tests can monkeypatch `DB_PATH`
    without being affected by a default parameter bound at import time.

    `check_same_thread=False` is only intended for a single long-lived connection that
    is explicitly synchronized (e.g. the API's shared connection guarded by a lock).
    """
    if path is None:
        path = DB_PATH
    connection = sqlite3.connect(path, timeout=timeout, check_same_thread=check_same_thread)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON;")
    return connection


def initialize_database(path: Path | str = DB_PATH) -> Path:
    """Initialize the SQLite database file and apply all pending schema migrations."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with connect_db(path) as connection:
        run_migrations(connection, MIGRATIONS_DIR)
    return path


# ---------------------------------------------------------------------------
#  INSERT FUNCTIONS
# ---------------------------------------------------------------------------

def insert_index_daily(
    index_name: str,
    date,
    open: float | None,
    high: float | None,
    low: float | None,
    close: float | None,
    change_pct: float | None = None,
    turnover: float | None = None,
    currency: str | None = None,
    path: Path | str | None = None,
):
    """Insert one INDEX_DAILY row into SQLite."""
    with connect_db(path) as conn:
        conn.execute(
            """
            INSERT INTO indexes_daily (
                index_name, date, open, high, low, close, change_pct, turnover, currency
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                index_name,
                date,
                open,
                high,
                low,
                close,
                change_pct,
                turnover,
                currency,
            ),
        )
        conn.commit()


def insert_ticker(
    ticker: str,
    name: str | None = None,
    sector: str | None = None,
    market: str | None = None,
    path: Path | str | None = None,
):
    """Insert or update a TICKER_MAP row into SQLite (upsert by ticker)."""
    with connect_db(path) as conn:
        conn.execute(
            """
            INSERT INTO tickers (ticker, name, sector, market)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(ticker) DO UPDATE SET
                name = excluded.name,
                sector = excluded.sector,
                market = excluded.market
            """,
            (ticker, name, sector, market),
        )
        conn.commit()


def insert_sector_company(
    sector: str,
    ticker: str,
    company_name: str | None = None,
    path: Path | str | None = None,
):
    """Insert or update a SECTOR_COMPOSITION row into SQLite (upsert by sector+ticker)."""
    with connect_db(path) as conn:
        conn.execute(
            """
            INSERT INTO sector_companies (sector, ticker, company_name)
            VALUES (?, ?, ?)
            ON CONFLICT(sector, ticker) DO UPDATE SET
                company_name = excluded.company_name
            """,
            (sector, ticker, company_name),
        )
        conn.commit()


def insert_sector_index_map(
    sector: str,
    index_name: str,
    path: Path | str | None = None,
):
    """Insert a SECTOR_INDEX_MAP row into SQLite, ignoring duplicates (sector+index_name)."""
    with connect_db(path) as conn:
        conn.execute(
            """
            INSERT INTO sector_index_map (sector, index_name)
            VALUES (?, ?)
            ON CONFLICT(sector, index_name) DO NOTHING
            """,
            (sector, index_name),
        )
        conn.commit()


def insert_recommendation(
    ticker: str,
    published_at: str,
    company_name: str | None = None,
    recommendation: str | None = None,
    target_price: float | None = None,
    current_price: float | None = None,
    potential_pct: float | None = None,
    price_at_issue: float | None = None,
    author: str | None = None,
    source_url: str | None = None,
    path: Path | str | None = None,
):
    """Insert or update a scraped recommendation row (upsert by ticker+published_at+author)."""
    with connect_db(path) as conn:
        conn.execute(
            """
            INSERT INTO recommendations (
                ticker, company_name, recommendation, target_price, current_price,
                potential_pct, price_at_issue, published_at, author, source_url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(ticker, published_at, author) DO UPDATE SET
                company_name = excluded.company_name,
                recommendation = excluded.recommendation,
                target_price = excluded.target_price,
                current_price = excluded.current_price,
                potential_pct = excluded.potential_pct,
                price_at_issue = excluded.price_at_issue,
                source_url = excluded.source_url
            """,
            (
                ticker,
                company_name,
                recommendation,
                target_price,
                current_price,
                potential_pct,
                price_at_issue,
                published_at,
                author,
                source_url,
            ),
        )
        conn.commit()


def upsert_financial_report(
    *,
    file_name: str,
    file_hash: str,
    ticker: str | None,
    company_name: str | None,
    report_type: str | None,
    period_start: str | None,
    period_end: str | None,
    currency: str | None,
    metrics: list[dict],
    path: Path | str | None = None,
) -> int:
    """Store one parsed report and replace its metrics atomically."""
    with connect_db(path) as conn:
        conn.execute(
            """
            INSERT INTO financial_reports (
                file_name, file_hash, ticker, company_name, report_type,
                period_start, period_end, currency
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(file_hash) DO UPDATE SET
                file_name = excluded.file_name,
                ticker = excluded.ticker,
                company_name = excluded.company_name,
                report_type = excluded.report_type,
                period_start = excluded.period_start,
                period_end = excluded.period_end,
                currency = excluded.currency
            """,
            (file_name, file_hash, ticker, company_name, report_type, period_start, period_end, currency),
        )
        report_id = conn.execute(
            "SELECT id FROM financial_reports WHERE file_hash = ?", (file_hash,)
        ).fetchone()["id"]
        conn.execute("DELETE FROM financial_metrics WHERE report_id = ?", (report_id,))
        conn.executemany(
            """
            INSERT INTO financial_metrics (
                report_id, metric_name, value, period_start, period_end, currency,
                unit, source_page, source_quote, confidence
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    report_id,
                    metric["metric_name"],
                    metric["value"],
                    metric.get("period_start"),
                    metric.get("period_end"),
                    metric.get("currency") or currency,
                    metric.get("unit"),
                    metric.get("source_page"),
                    metric.get("source_quote"),
                    metric.get("confidence"),
                )
                for metric in metrics
            ],
        )
        conn.commit()
        return report_id


if __name__ == "__main__":
    db_file = initialize_database()
    print(f"Initialized AGPW database at: {db_file}")
