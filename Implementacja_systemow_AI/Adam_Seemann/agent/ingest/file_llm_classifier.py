import json
import logging
import subprocess  # nosec B404 - used to call local Ollama CLI for optional LLM fallback
from pathlib import Path
from typing import Literal, cast

FileType = Literal[
    "STOCK_DAILY",
    "INDEX_DAILY",
    "TICKER_MAP",
    "SECTOR_COMPOSITION",
    "SECTOR_INDEX_MAP",
    "UNKNOWN",
]


def _heuristic_classify(df) -> FileType:
    """Fallback heuristics when LLM fails or is uncertain."""
    lower_cols = {str(col).strip().lower() for col in df.columns}

    # --- GPW STOCK DAILY ---
    # ISIN + Kurs zamknięcia → zawsze akcje
    if "isin" in lower_cols and (
        "kurs zamknięcia" in lower_cols or "kurs zamkniecia" in lower_cols
    ):
        return "STOCK_DAILY"

    # --- GPW INDEX DAILY ---
    # Nazwa + Kurs zamknięcia → indeks
    if "nazwa" in lower_cols and (
        "kurs zamknięcia" in lower_cols or "kurs zamkniecia" in lower_cols
    ):
        return "INDEX_DAILY"

    # --- English STOCK_DAILY ---
    if {"date", "open", "high", "low", "close", "volume"}.issubset(lower_cols):
        return "STOCK_DAILY"

    # --- English INDEX_DAILY ---
    if {"date", "open", "high", "low", "close"}.issubset(lower_cols):
        return "INDEX_DAILY"

    # --- Other formats ---
    if {"ticker", "name"}.issubset(lower_cols):
        return "TICKER_MAP"

    if {"sector", "ticker"}.issubset(lower_cols):
        return "SECTOR_COMPOSITION"

    if {"sector", "index_name"}.issubset(lower_cols):
        return "SECTOR_INDEX_MAP"

    return "UNKNOWN"


def classify_file(path: Path, df) -> FileType:
    """Classify an Excel file using local LLM (Phi-3) with heuristic fallback."""

    # --- 1. Heurystyka ma pierwszeństwo ---
    heuristic = _heuristic_classify(df)
    if heuristic != "UNKNOWN":
        return heuristic

    # --- 2. Dopiero potem LLM ---
    cols = list(df.columns)
    sample = df.head(5).to_dict(orient="records")

    prompt = f"""
    You are a classifier for financial Excel files.

    Decide the file type based on columns, file name, and sample rows.
    Allowed types:
    STOCK_DAILY
    INDEX_DAILY
    TICKER_MAP
    SECTOR_COMPOSITION
    SECTOR_INDEX_MAP
    UNKNOWN

    Respond with ONLY the type name.

    File name: {path.name}
    Columns: {cols}
    Sample rows: {json.dumps(sample)}
    """

    try:
        # Safe: fixed local executable name, no shell, prompt passed via stdin (not shell args).
        result = subprocess.run(  # nosec B603 B607
            ["ollama", "run", "phi3"],
            input=prompt.encode(),
            capture_output=True,
            timeout=5,
        )
        llm_output = result.stdout.decode().strip().upper()

        allowed_types: set[FileType] = {
            "STOCK_DAILY",
            "INDEX_DAILY",
            "TICKER_MAP",
            "SECTOR_COMPOSITION",
            "SECTOR_INDEX_MAP",
            "UNKNOWN",
        }
        if llm_output in allowed_types:
            return cast(FileType, llm_output)

    except Exception:
        logging.getLogger(__name__).debug("LLM classification unavailable, falling back to heuristics", exc_info=True)

    # --- 3. fallback heurystyka ---
    return _heuristic_classify(df)
