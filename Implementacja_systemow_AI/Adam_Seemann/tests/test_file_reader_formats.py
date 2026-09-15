import json
from pathlib import Path

import pandas as pd
import pytest

from agent.ingest.file_reader import read_csv_file, read_file, read_json_file, validate_dataframe


def test_read_csv_file_comma(tmp_path: Path):
    path = tmp_path / "stock.csv"
    path.write_text(
        "ISIN,Date,Open,High,Low,Close,Volume\n"
        "PLAAA0000001,2026-08-01,100.0,110.0,99.0,108.0,1000\n",
        encoding="utf-8",
    )

    df = read_csv_file(path)
    assert list(df.columns) == ["ISIN", "Date", "Open", "High", "Low", "Close", "Volume"]
    assert df.shape == (1, 7)


def test_read_csv_file_semicolon_polish_encoding(tmp_path: Path):
    path = tmp_path / "stock_pl.csv"
    content = "ISIN;Nazwa;Kurs zamknięcia\nPLAAA0000001;Spółka A;108,50\n"
    path.write_bytes(content.encode("cp1250"))

    df = read_csv_file(path)
    assert list(df.columns) == ["ISIN", "Nazwa", "Kurs zamknięcia"]
    assert df.loc[0, "Nazwa"] == "Spółka A"


def test_read_json_file_list_of_records(tmp_path: Path):
    path = tmp_path / "stock.json"
    records = [
        {"isin": "PLAAA0000001", "date": "2026-08-01", "open": 100.0, "close": 108.0},
        {"isin": "PLAAA0000001", "date": "2026-08-02", "open": 108.0, "close": 110.0},
    ]
    path.write_text(json.dumps(records), encoding="utf-8")

    df = read_json_file(path)
    assert df.shape == (2, 4)
    assert df.loc[0, "isin"] == "PLAAA0000001"


def test_read_json_file_data_wrapper(tmp_path: Path):
    path = tmp_path / "stock_wrapped.json"
    payload = {"data": [{"ticker": "AAA", "name": "Company A"}]}
    path.write_text(json.dumps(payload), encoding="utf-8")

    df = read_json_file(path)
    assert df.shape == (1, 2)
    assert df.loc[0, "ticker"] == "AAA"


def test_read_json_file_invalid_raises(tmp_path: Path):
    path = tmp_path / "broken.json"
    path.write_text("{not valid json", encoding="utf-8")

    with pytest.raises(ValueError):
        read_json_file(path)


def test_read_file_dispatches_by_extension(tmp_path: Path):
    csv_path = tmp_path / "a.csv"
    csv_path.write_text("ticker,name\nAAA,Company A\n", encoding="utf-8")
    df = read_file(csv_path)
    assert df.shape == (1, 2)

    json_path = tmp_path / "a.json"
    json_path.write_text(json.dumps([{"ticker": "AAA", "name": "Company A"}]), encoding="utf-8")
    df = read_file(json_path)
    assert df.shape == (1, 2)

    with pytest.raises(ValueError):
        read_file(tmp_path / "a.txt")


def test_validate_dataframe_rejects_duplicate_columns(tmp_path: Path):
    df = pd.DataFrame([[1, 2]], columns=["ticker", "Ticker"])
    with pytest.raises(ValueError):
        validate_dataframe(df, tmp_path / "dup.csv")


def test_validate_dataframe_rejects_unnamed_columns(tmp_path: Path):
    df = pd.DataFrame([[1, 2]], columns=["ticker", "Unnamed: 1"])
    with pytest.raises(ValueError):
        validate_dataframe(df, tmp_path / "unnamed.csv")


def test_validate_dataframe_drops_fully_empty_rows(tmp_path: Path):
    df = pd.DataFrame({"ticker": ["AAA", None], "name": ["Company A", None]})
    cleaned = validate_dataframe(df, tmp_path / "sparse.csv")
    assert cleaned.shape == (1, 2)
