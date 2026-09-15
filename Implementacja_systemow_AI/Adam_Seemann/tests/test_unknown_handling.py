import shutil

import pandas as pd

from agent.ingest import file_router
from data import db


def test_unknown_moves_file(tmp_path, monkeypatch):
    # Setup temp incoming dir
    incoming = tmp_path / "incoming"
    incoming.mkdir()
    # create an xlsx with headers that should classify as UNKNOWN (e.g., 'Data','Nazwa',...)
    df = pd.DataFrame([[1, 'X', 'PLXXX', 'PLN']], columns=['Data', 'Nazwa', 'ISIN', 'Waluta'])
    file_path = incoming / "unknown_sample.xlsx"
    df.to_excel(file_path, index=False)

    # Use temp DB
    db_path = tmp_path / "agpw.db"
    monkeypatch.setattr(db, 'DB_PATH', db_path)
    db.initialize_database(db_path)

    # Run ingest_directory
    file_router.ingest_directory(incoming)

    # Expect file moved to incoming/unknown
    unknown_dir = incoming / 'unknown'
    assert unknown_dir.exists()
    moved = list(unknown_dir.glob('unknown_sample.*'))
    assert moved, 'Unknown file not moved'

    # Clean up
    shutil.rmtree(str(incoming))
