import argparse
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from data.db import initialize_database

from .file_router import ingest_directory

# Configure logging: console + rotating file handler in project logs/ingest.log
ROOT_DIR = Path(__file__).resolve().parents[2]
LOG_DIR = ROOT_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "ingest.log"

formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
file_handler = RotatingFileHandler(str(LOG_FILE), maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8")
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(file_handler)
root_logger.addHandler(stream_handler)

logger = logging.getLogger("agpw.ingest")


def main():
    parser = argparse.ArgumentParser(description="Run AGPW ingest on a directory of Excel files.")
    parser.add_argument("--dir", "-d", default="data/incoming", help="Directory to scan for Excel files")
    args = parser.parse_args()

    directory = Path(args.dir)
    # ensure database and tables exist before ingest
    initialize_database()
    logger.info("Starting ingest for directory: %s", directory)
    ingest_directory(directory)
    logger.info("Ingest run finished for directory: %s", directory)


if __name__ == "__main__":
    main()
