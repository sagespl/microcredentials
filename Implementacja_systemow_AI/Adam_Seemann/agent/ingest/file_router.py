import logging
import shutil
from pathlib import Path

from .file_llm_classifier import classify_file
from .file_reader import read_file
from .ingest_financial_report import ingest_financial_report
from .ingest_indexes_daily import ingest_indexes_daily
from .ingest_sector_composition import ingest_sector_composition
from .ingest_sector_index_map import ingest_sector_index_map
from .ingest_stocks_daily import ingest_stocks_daily
from .ingest_ticker_map import ingest_ticker_map

logger = logging.getLogger(__name__)

INGESTORS = {
    "STOCK_DAILY": ingest_stocks_daily,
    "INDEX_DAILY": ingest_indexes_daily,
    "TICKER_MAP": ingest_ticker_map,
    "SECTOR_COMPOSITION": ingest_sector_composition,
    "SECTOR_INDEX_MAP": ingest_sector_index_map,
}


def ingest_file(path: Path) -> None:
    """Ingest a single file and move it to loaded/ or unknown/."""
    try:
        if path.suffix.lower() == ".pdf":
            report_id = ingest_financial_report(path)
            logger.info("Ingested financial report %s from %s", report_id, path.name)
            _move_to_loaded(path)
            return

        df = read_file(path)
        file_type = classify_file(path, df)

        ingestor = INGESTORS.get(file_type)
        if ingestor is None:
            if path.suffix.lower() in {".xlsx", ".xls"}:
                report_id = ingest_financial_report(path)
                logger.info("Ingested financial report %s from %s", report_id, path.name)
                _move_to_loaded(path)
                return
            raise ValueError(f"Unsupported file type: {file_type}")

        row_count = ingestor(df, path)
        logger.info("Ingested %s rows from %s", row_count, path.name)

        _move_to_loaded(path)

    except Exception as e:
        logger.error("Failed to ingest %s: %s", path.name, e)

        # Move to unknown/
        unknown_dir = path.parent / "unknown"
        unknown_dir.mkdir(exist_ok=True)
        shutil.move(str(path), unknown_dir / path.name)


def _move_to_loaded(path: Path) -> None:
    loaded_dir = path.parent / "loaded"
    loaded_dir.mkdir(exist_ok=True)
    shutil.move(str(path), loaded_dir / path.name)


def ingest_directory(directory: Path) -> None:
    """Ingest all files in the given directory."""
    incoming = Path(directory)

    for path in incoming.glob("*"):
        if path.is_file():
            ingest_file(path)
