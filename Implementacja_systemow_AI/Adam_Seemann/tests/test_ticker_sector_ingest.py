import pandas as pd

from agent.ingest.ingest_sector_composition import ingest_sector_composition
from agent.ingest.ingest_sector_index_map import ingest_sector_index_map
from agent.ingest.ingest_ticker_map import ingest_ticker_map
from data import db


def _init_db(tmp_path, monkeypatch):
    db_path = tmp_path / "agpw.db"
    monkeypatch.setattr(db, "DB_PATH", db_path)
    db.initialize_database(db_path)
    return db_path


def test_ingest_ticker_map_upsert(tmp_path, monkeypatch):
    db_path = _init_db(tmp_path, monkeypatch)

    df = pd.DataFrame([
        {"ticker": "AGPW", "name": "AGPW SA", "sector": "IT", "market": "GPW"},
        {"ticker": "AGPW", "name": "AGPW SA Updated", "sector": "IT", "market": "GPW"},
    ])
    count = ingest_ticker_map(df, tmp_path / "ticker_map.xlsx")
    assert count == 2

    conn = db.connect_db(db_path)
    rows = conn.execute("SELECT ticker, name FROM tickers WHERE ticker = ?", ("AGPW",)).fetchall()
    assert len(rows) == 1
    assert rows[0]["name"] == "AGPW SA Updated"
    conn.close()


def test_ingest_sector_composition(tmp_path, monkeypatch):
    db_path = _init_db(tmp_path, monkeypatch)

    df = pd.DataFrame([
        {"sector": "IT", "ticker": "AGPW", "company_name": "AGPW SA"},
        {"sector": "IT", "ticker": "XYZ", "company_name": "XYZ SA"},
    ])
    count = ingest_sector_composition(df, tmp_path / "sector_composition.xlsx")
    assert count == 2

    conn = db.connect_db(db_path)
    rows = conn.execute("SELECT sector, ticker FROM sector_companies").fetchall()
    assert len(rows) == 2
    conn.close()


def test_ingest_sector_index_map(tmp_path, monkeypatch):
    db_path = _init_db(tmp_path, monkeypatch)

    df = pd.DataFrame([
        {"sector": "IT", "index_name": "WIG20"},
        {"sector": "IT", "index_name": "WIG20"},
    ])
    count = ingest_sector_index_map(df, tmp_path / "sector_index_map.xlsx")
    assert count == 2

    conn = db.connect_db(db_path)
    rows = conn.execute("SELECT sector, index_name FROM sector_index_map").fetchall()
    assert len(rows) == 1
    conn.close()
