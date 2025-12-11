import io
import logging

from web_app.antivirus.clamav.connector import ClamavConnector


class AntivirusScanner:
    def __init__(self, connector: ClamavConnector):
        self.connector = connector

    def scan(self, file: bytes) -> None:
        logging.info("Scanning file with Clamav")
        input_stream = io.BytesIO(file)
        result = self.connector.socket.instream(input_stream)

        if result["stream"][0] != "OK":
            raise ValueError(f"Virus detected: {result['stream'][1]}")

        logging.info("Scanning file with Clamav")
