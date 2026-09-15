
import pandas as pd

from agent.ingest import file_router
from data import db


def test_real_file_ingest(tmp_path, monkeypatch):
    incoming = tmp_path / "incoming"
    incoming.mkdir()

    df = pd.DataFrame({
        "Ticker": ["AAA", "BBB"],
        "ISIN": ["PLAAA0000001", "PLBBB0000002"],
        "Date": ["2026-08-10", "2026-08-11"],
        "Open": [100.0, 105.0],
        "High": [110.0, 108.0],
        "Low": [99.0, 103.0],
        "Close": [108.0, 107.0],
    })
    file_path = incoming / "real_akcje.xlsx"
    df.to_excel(file_path, index=False)

    # Wymuszenie klasyfikacji jako stocks_daily
    monkeypatch.setattr(
        file_router,
        "classify_file",
        lambda _, __: "STOCK_DAILY",
    )

    # Użycie tymczasowej bazy
    db_path = tmp_path / "agpw.db"
    monkeypatch.setattr(db, "DB_PATH", db_path)
    db.initialize_database(db_path)

    # Uruchom ingest
    file_router.ingest_directory(incoming)

    # Plik powinien zostać usunięty po poprawnym ingescie
    assert not file_path.exists(), "Input file should be deleted after ingest"

    # W bazie powinny być dwa rekordy
    conn = db.connect_db(db_path)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as c FROM stocks_daily")
    cnt = cur.fetchone()["c"]
    conn.close()
    assert cnt == 2
