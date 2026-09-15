import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pandas as pd


def write_excel(path: Path, columns: list, row: dict):
    df = pd.DataFrame([row], columns=columns)
    df.to_excel(path, index=False)

def run_ingest(tmpdir: Path):
    cmd = [
        sys.executable,
        "-m",
        "agent.ingest.run_ingest",
        "--dir",
        str(tmpdir)
    ]
    return subprocess.run(cmd, capture_output=True, text=True)

def test_ingest_moves_loaded_and_unknown():
    tmpdir = Path(tempfile.mkdtemp())
    incoming = tmpdir
    loaded = incoming / "loaded"
    unknown = incoming / "unknown"

    # 1) Poprawny plik STOCK_DAILY
    stock_file = incoming / "stock.xlsx"
    write_excel(
        stock_file,
        ["ISIN", "Date", "Open", "High", "Low", "Close", "Volume"],
        {"ISIN": "PLAAA0000001", "Date": "2024-01-01", "Open": 1, "High": 2, "Low": 0.5, "Close": 1.5, "Volume": 1000}
    )

    # 2) Plik UNKNOWN
    unknown_file = incoming / "unknown.xlsx"
    write_excel(
        unknown_file,
        ["AAA", "BBB", "CCC"],
        {"AAA": 1, "BBB": 2, "CCC": 3}
    )

    result = run_ingest(incoming)
    print(result.stdout)
    print(result.stderr)

    assert loaded.exists(), "Brak katalogu loaded/"
    assert unknown.exists(), "Brak katalogu unknown/"

    assert (loaded / "stock.xlsx").exists(), "Poprawny plik nie został przeniesiony do loaded/"
    assert (unknown / "unknown.xlsx").exists(), "Plik UNKNOWN nie został przeniesiony do unknown/"

    remaining = list(incoming.glob("*.xlsx"))
    assert len(remaining) == 0, f"Pliki pozostały w incoming/: {remaining}"

    shutil.rmtree(tmpdir)
