import hashlib
import logging


def calculate_hash(file: bytes) -> str:
    logging.info("Calculating hash of file")
    file_hash = hashlib.sha256(file).hexdigest()
    logging.info("Hash of file calculated successfully.")
    return file_hash
