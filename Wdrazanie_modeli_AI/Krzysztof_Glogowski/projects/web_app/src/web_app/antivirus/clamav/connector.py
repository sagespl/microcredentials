import logging

import clamd

from web_app.utils.error import ClamavConnectionNotAliveError, ClamavConnectionError


class ClamavConnector:
    def __init__(self, host: str = "127.0.0.1", port: int = 3310):
        self.host = host
        self.port = port
        self.socket = self._create_socket(host, port)

    def is_alive(self):
        logging.debug(f"Checking if connection to Clamav on {self.host=}, {self.port=} is alive.")
        try:
            self.socket.ping()
        except clamd.ConnectionError as e:
            logging.exception("Connection to Clamav is not alive.")
            raise ClamavConnectionNotAliveError(self.host, self.port) from e

    @staticmethod
    def _create_socket(host: str, port: int) -> clamd.ClamdNetworkSocket:
        logging.info(f"Creating connection to Clamav on {host=}, {port=}.")
        try:
            socket = clamd.ClamdNetworkSocket(host=host, port=port)
            socket.ping()
        except clamd.ConnectionError as e:
            logging.exception("Unable to connect to Clamav.")
            raise ClamavConnectionError(host, port) from e
        logging.info("Successfully created connection to Clamav.")
        return socket
