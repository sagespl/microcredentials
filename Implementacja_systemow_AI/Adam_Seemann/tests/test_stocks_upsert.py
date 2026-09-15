
import pandas as pd

from agent.ingest import ingest_stocks_daily
from data import db


def test_upsert_by_isin_date(tmp_path, monkeypatch):
    incoming = tmp_path / 'incoming'
    incoming.mkdir()
    # Create sample file with two rows same isin/date, different ticker to test upsert
    df = pd.DataFrame([
        {'ISIN': 'PLXXX0001', 'Data': '2026-08-11', 'Kurs otwarcia': 10.0, 'Kurs max': 11.0, 'Kurs min': 9.5, 'Kurs zamknięcia': 10.5, 'Nazwa':'A', 'Waluta':'PLN', 'Liczba Transakcji':1},
        {'ISIN': 'PLXXX0001', 'Data': '2026-08-11', 'Kurs otwarcia': 10.1, 'Kurs max': 11.1, 'Kurs min': 9.6, 'Kurs zamknięcia': 10.6, 'Nazwa':'B', 'Waluta':'PLN', 'Liczba Transakcji':2},
    ])
    file_path = incoming / 'stocks.xlsx'
    df.to_excel(file_path, index=False)

    # Use temp DB
    db_path = tmp_path / 'agpw.db'
    monkeypatch.setattr(db, 'DB_PATH', db_path)
    db.initialize_database(db_path)

    # Read file and call ingest function
    df_read = pd.read_excel(file_path)
    # First ingest
    count = ingest_stocks_daily.ingest_stocks_daily(df_read, file_path)
    assert count == 2

    # Query DB to ensure only one row exists for that isin/date and that it's the last inserted values
    conn = db.connect_db(db_path)
    cur = conn.cursor()
    cur.execute("SELECT ticker, isin, date, open FROM stocks_daily WHERE isin = ?", ('PLXXX0001',))
    rows = cur.fetchall()
    assert len(rows) == 1
    # The stored open should be 10.1 (from second row)
    assert abs(rows[0]['open'] - 10.1) < 1e-6
    conn.close()
