import threading

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from agent.ingest.ingest_stocks_daily import ingest_stocks_daily
from api.database import DatabaseSession, get_db_session
from api.server import app
from data import db


@pytest.fixture(scope="module")
def client():
    # Entering as a context manager runs the app's lifespan (startup/shutdown).
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def test_db(tmp_path, monkeypatch):
    """Isolated SQLite DB used by both ingest helpers and the API's DB dependency."""
    db_path = tmp_path / "agpw.db"
    monkeypatch.setattr(db, "DB_PATH", db_path)
    db.initialize_database(db_path)

    connection = db.connect_db(db_path, check_same_thread=False)
    session = DatabaseSession(connection=connection, lock=threading.Lock())
    app.dependency_overrides[get_db_session] = lambda: session
    try:
        yield db_path
    finally:
        app.dependency_overrides.pop(get_db_session, None)
        connection.close()


def test_health_endpoint_returns_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_ready_endpoint_returns_ok(client, test_db):
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}


def test_metrics_endpoint_exposes_prometheus_format(client):
    client.get("/health")  # ensure at least one request has been recorded
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "agpw_http_requests_total" in response.text


def test_stock_endpoint_returns_quotes_and_score(client, test_db):
    db_path = test_db
    ingest_stocks_daily(
        pd.DataFrame(
            [
                {"isin": "PLTEST", "date": f"2026-08-{day:02d}", "open": 100 + day,
                 "high": 102 + day, "low": 98 + day, "close": 101 + day,
                 "volume": 4_000 if day == 40 else 1_000}
                for day in range(1, 41)
            ]
        ),
        db_path.parent / "sample.xlsx",
    )

    response = client.get("/api/stocks/PLTEST")
    assert response.status_code == 200
    assert len(response.json()) == 40

    filtered_response = client.get(
        "/api/stocks/PLTEST?start_date=2026-08-10&end_date=2026-08-20"
    )
    assert filtered_response.status_code == 200
    assert len(filtered_response.json()) == 11

    score_response = client.get("/api/score/PLTEST")
    assert score_response.status_code == 200
    score_payload = score_response.json()
    assert 0 <= score_payload["score"]["score"] <= 100
    assert score_payload["analysis"]["rows"] == 40
    assert any(anomaly["type"] == "spike" for anomaly in score_payload["anomalies"])

    report_response = client.get("/api/report/PLTEST")
    assert report_response.status_code == 200
    report_payload = report_response.json()
    assert report_payload["ticker"] == "PLTEST"
    assert "PLTEST: technical score" in report_payload["report"]
    assert "Financial score unavailable." in report_payload["report"]


def test_stock_endpoint_returns_404_for_unknown_stock(client, test_db):
    response = client.get("/api/stocks/UNKNOWN")
    assert response.status_code == 404


def test_ticker_map_endpoint_returns_known_tickers(client, test_db):
    db_path = test_db
    db.insert_ticker("AGPW", name="AGPW S.A.", sector="Finance", path=db_path)

    response = client.get("/api/ticker-map")

    assert response.status_code == 200
    assert response.json() == [
        {"ticker": "AGPW", "name": "AGPW S.A.", "sector": "Finance", "market": None}
    ]


def test_index_endpoint_returns_filtered_quotes(client, test_db):
    db_path = test_db
    for day in range(1, 4):
        db.insert_index_daily(
            "WIG20",
            f"2026-08-{day:02d}",
            2000 + day,
            2020 + day,
            1990 + day,
            2010 + day,
            path=db_path,
        )

    response = client.get("/api/indices/wig20?start_date=2026-08-02")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["index_name"] == "WIG20"

    invalid_range = client.get(
        "/api/indices/WIG20?start_date=2026-08-03&end_date=2026-08-01"
    )
    assert invalid_range.status_code == 400
