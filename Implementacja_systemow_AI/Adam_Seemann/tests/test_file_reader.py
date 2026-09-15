from pathlib import Path

import pandas as pd

from agent.ingest.file_reader import read_excel_file


def test_read_excel_file(tmp_path: Path):
    file_path = tmp_path / "sample.xlsx"
    df = pd.DataFrame(
        {
            "Ticker": ["AAA", "BBB"],
            "ISIN": ["PLAAA0000001", "PLBBB0000002"],
            "Date": ["2026-08-01", "2026-08-02"],
            "Open": [100.0, 105.0],
            "High": [110.0, 108.0],
            "Low": [99.0, 103.0],
            "Close": [108.0, 107.0],
        }
    )
    df.to_excel(file_path, index=False)

    result = read_excel_file(file_path)

    assert result.shape == (2, 7)
    assert list(result.columns) == ["Ticker", "ISIN", "Date", "Open", "High", "Low", "Close"]
    assert result.loc[0, "Ticker"] == "AAA"
