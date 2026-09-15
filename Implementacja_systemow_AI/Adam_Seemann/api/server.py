import logging
from datetime import date
from logging.handlers import RotatingFileHandler
from pathlib import Path

import pandas as pd
from fastapi import Depends, FastAPI, HTTPException, Response

from agent.agents import (
    analyze_data,
    detect_anomalies,
    detect_volume_anomalies,
    generate_report,
    score_company,
)
from api.database import DatabaseSession, get_db_session
from api.lifespan import lifespan
from api.metrics import CONTENT_TYPE_LATEST, render_latest
from api.middlewares import setup_middlewares

# --- Logging: console + rotating file handler in logs/api.log ---
LOG_DIR = Path(__file__).resolve().parents[1] / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("agpw.api")
if not logger.handlers:
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    file_handler = RotatingFileHandler(
        str(LOG_DIR / "api.log"), maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.setLevel(logging.INFO)

app = FastAPI(lifespan=lifespan)
setup_middlewares(app)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/health/ready")
def health_ready(db: DatabaseSession = Depends(get_db_session)):
    """Readiness check: verifies the SQLite database is reachable."""
    try:
        db.execute_one("SELECT 1")
        return {"status": "ok", "database": "ok"}
    except Exception as e:
        logger.error("Readiness check failed: %s", e)
        raise HTTPException(status_code=503, detail="Database unavailable") from e


@app.get("/metrics")
def metrics():
    """Expose Prometheus metrics for scraping."""
    return Response(content=render_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/api/stocks/{ticker}")
def get_stock_data(
    ticker: str,
    start_date: date | None = None,
    end_date: date | None = None,
    db: DatabaseSession = Depends(get_db_session),
):
    """Return daily stock quotes identified by ticker or ISIN."""
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date must not be after end_date")

    filters = [
        "(UPPER(COALESCE(ticker, '')) = UPPER(?) OR UPPER(isin) = UPPER(?))"
    ]
    parameters: list[str] = [ticker, ticker]
    if start_date:
        filters.append("date >= ?")
        parameters.append(start_date.isoformat())
    if end_date:
        filters.append("date <= ?")
        parameters.append(end_date.isoformat())

    # Safe: filters are fixed static SQL fragments, all values are bound `?` parameters.
    rows = db.execute(
        f"""
        SELECT ticker, name, isin, date, open, high, low, close,
               volume, num_trades, change_pct, turnover, currency
        FROM stocks_daily
        WHERE {' AND '.join(filters)}
        ORDER BY date
        """,  # nosec B608
        parameters,
    )

    if not rows:
        raise HTTPException(status_code=404, detail=f"Stock not found: {ticker}")
    return [dict(row) for row in rows]


@app.get("/api/ticker-map")
def get_ticker_map(db: DatabaseSession = Depends(get_db_session)):
    """Return the known ticker map for the frontend search."""
    rows = db.execute("SELECT ticker, name, sector, market FROM tickers ORDER BY ticker")
    return [dict(row) for row in rows]


@app.get("/api/indices/{index_name}")
def get_index_data(
    index_name: str,
    start_date: date | None = None,
    end_date: date | None = None,
    db: DatabaseSession = Depends(get_db_session),
):
    """Return daily index quotes with optional date filtering."""
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date must not be after end_date")

    filters = ["UPPER(index_name) = UPPER(?)"]
    parameters: list[str] = [index_name]
    if start_date:
        filters.append("date >= ?")
        parameters.append(start_date.isoformat())
    if end_date:
        filters.append("date <= ?")
        parameters.append(end_date.isoformat())

    # Safe: filters are fixed static SQL fragments, all values are bound `?` parameters.
    rows = db.execute(
        f"""
        SELECT index_name, date, open, high, low, close,
               change_pct, turnover, currency
        FROM indexes_daily
        WHERE {' AND '.join(filters)}
        ORDER BY date
        """,  # nosec B608
        parameters,
    )

    if not rows:
        raise HTTPException(status_code=404, detail=f"Index not found: {index_name}")
    return [dict(row) for row in rows]


@app.get("/api/score/{ticker}")
def get_stock_score(
    ticker: str,
    start_date: date | None = None,
    end_date: date | None = None,
    db: DatabaseSession = Depends(get_db_session),
):
    """Return technical indicators, anomalies and score for a stock."""
    quotes = get_stock_data(ticker, start_date, end_date, db)
    analysis_data = [
        {
            "close": quote["close"],
            "high": quote["high"],
            "low": quote["low"],
            "volume": quote["volume"],
        }
        for quote in quotes
    ]

    analysis = analyze_data(pd.DataFrame(analysis_data))
    analysis_frame = pd.DataFrame(analysis_data)
    anomalies = detect_anomalies(analysis_frame)
    anomalies.extend(detect_volume_anomalies(analysis_frame))
    score = score_company(analysis, anomalies)
    return {"ticker": ticker, "analysis": analysis, "anomalies": anomalies, "score": score}


@app.get("/api/report/{ticker}")
def get_stock_report(
    ticker: str,
    start_date: date | None = None,
    end_date: date | None = None,
    db: DatabaseSession = Depends(get_db_session),
):
    """Return a human-readable report based on available stock quote data."""
    score_data = get_stock_score(ticker, start_date, end_date, db)
    return {
        "ticker": ticker,
        "report": generate_report(
            ticker,
            score_data["score"],
            anomalies=score_data["anomalies"],
        ),
    }
