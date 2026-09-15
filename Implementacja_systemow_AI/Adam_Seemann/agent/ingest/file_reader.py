import csv
import json
import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

SUPPORTED_EXCEL_EXTENSIONS = {".xls", ".xlsx"}
SUPPORTED_CSV_EXTENSIONS = {".csv"}
SUPPORTED_JSON_EXTENSIONS = {".json"}
SUPPORTED_EXTENSIONS = SUPPORTED_EXCEL_EXTENSIONS | SUPPORTED_CSV_EXTENSIONS | SUPPORTED_JSON_EXTENSIONS

# Encodings to try in order when reading text-based files (Polish GPW exports
# are frequently saved as Windows-1250/ISO-8859-2 rather than UTF-8).
_TEXT_ENCODINGS = ("utf-8-sig", "cp1250", "iso-8859-2")


def validate_dataframe(df: pd.DataFrame, path: Path) -> pd.DataFrame:
    """Apply common structural validation/cleanup shared by all file formats.

    Raises ValueError for structurally broken files and returns a cleaned
    DataFrame (stripped column names, dropped fully-empty rows/columns).
    """
    if df is None or df.shape[1] == 0:
        raise ValueError(f"{path.name}: file contains no columns")

    df = df.rename(columns=lambda c: str(c).strip())

    if any(col == "" or col.lower().startswith("unnamed:") for col in df.columns):
        raise ValueError(f"{path.name}: file has missing or unnamed column headers")

    lower_cols = [c.lower() for c in df.columns]
    duplicates = {c for c in lower_cols if lower_cols.count(c) > 1}
    if duplicates:
        raise ValueError(f"{path.name}: duplicate column headers: {sorted(duplicates)}")

    # Drop rows that are entirely empty (common trailing blank rows in exports).
    df = df.dropna(how="all")

    if df.shape[0] == 0:
        raise ValueError(f"{path.name}: file contains no usable data rows")

    return df


def read_excel_file(path: Path) -> pd.DataFrame:
    """Read the first sheet from an Excel file and return a DataFrame."""
    path = Path(path)
    suffix = path.suffix.lower()

    if suffix not in SUPPORTED_EXCEL_EXTENSIONS:
        raise ValueError(f"Unsupported Excel extension: {suffix}")

    engine = "openpyxl" if suffix == ".xlsx" else "xlrd"
    logger.info("Reading Excel file %s with engine %s", path.name, engine)

    df = pd.read_excel(path, sheet_name=0, engine=engine)

    if df is None or df.shape[0] == 0:
        raise ValueError("Excel file contains no usable data")

    return validate_dataframe(df, path)


def _sniff_delimiter(sample: str) -> str:
    """Detect the CSV delimiter, defaulting to ',' when detection fails."""
    try:
        return csv.Sniffer().sniff(sample, delimiters=",;\t").delimiter
    except csv.Error:
        return ";" if sample.count(";") > sample.count(",") else ","


def read_csv_file(path: Path) -> pd.DataFrame:
    """Read a CSV file, auto-detecting encoding and delimiter."""
    path = Path(path)
    last_error: Exception | None = None

    for encoding in _TEXT_ENCODINGS:
        try:
            text = path.read_text(encoding=encoding)
        except (UnicodeDecodeError, LookupError) as e:
            last_error = e
            continue

        delimiter = _sniff_delimiter(text[:4096])
        logger.info("Reading CSV file %s with encoding %s and delimiter %r", path.name, encoding, delimiter)
        try:
            df = pd.read_csv(path, encoding=encoding, sep=delimiter)
        except Exception as e:
            last_error = e
            continue

        if df is None or df.shape[0] == 0:
            raise ValueError("CSV file contains no usable data")

        return validate_dataframe(df, path)

    raise ValueError(f"Could not decode CSV file {path.name}: {last_error}")


def read_json_file(path: Path) -> pd.DataFrame:
    """Read a JSON file containing a list of records or a records-oriented object."""
    path = Path(path)

    try:
        raw = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {path.name}: {e}") from e

    if isinstance(raw, dict):
        # Allow either {"data": [...]} wrappers or a plain records dict.
        raw = raw.get("data", raw) if "data" in raw else raw

    if isinstance(raw, dict):
        df = pd.DataFrame(raw)
    elif isinstance(raw, list):
        df = pd.DataFrame.from_records(raw)
    else:
        raise ValueError(f"{path.name}: unsupported JSON structure")

    if df is None or df.shape[0] == 0:
        raise ValueError("JSON file contains no usable data")

    return validate_dataframe(df, path)


def read_file(path: Path) -> pd.DataFrame:
    """
    Unified reader used by router + tests.
    Supports Excel (.xls, .xlsx), CSV (.csv) and JSON (.json) files.
    """
    path = Path(path)
    suffix = path.suffix.lower()

    if suffix in SUPPORTED_EXCEL_EXTENSIONS:
        return read_excel_file(path)
    if suffix in SUPPORTED_CSV_EXTENSIONS:
        return read_csv_file(path)
    if suffix in SUPPORTED_JSON_EXTENSIONS:
        return read_json_file(path)

    raise ValueError(f"Unsupported file type: {suffix}")

