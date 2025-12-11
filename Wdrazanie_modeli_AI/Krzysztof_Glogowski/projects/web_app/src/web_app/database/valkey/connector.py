import logging

import valkey

from web_app.utils.error import ValkeyConnectionNotAliveError, ValkeyConnectionError


class ValkeyConnector:
    def __init__(self, host: str = "127.0.0.1", port: int = 6379):
        self.host = host
        self.port = port
        self.connection: valkey.Valkey = self._create_connection(host, port)

    def close(self):
        self.connection.connection_pool.disconnect(inuse_connections=True)

    def is_alive(self):
        logging.debug(
            f"Checking if connection to Valkey database on {self.host=}, {self.port=} is alive."
        )
        try:
            self.connection.ping()
        except valkey.exceptions.ConnectionError as e:
            logging.exception("Connection to Valkey database is not alive.")
            raise ValkeyConnectionNotAliveError(self.host, self.port) from e
        logging.debug("Connection to Valkey database is alive.")

    @staticmethod
    def _create_connection(host: str, port: int) -> valkey.Valkey:
        logging.info(f"Creating connection to Valkey database on {host=}, {port=}.")
        try:
            connection = valkey.Valkey(host=host, port=port, protocol=3)
            connection.ping()
        except valkey.exceptions.ConnectionError as e:
            logging.exception("Unable to connect to Valkey database.")
            raise ValkeyConnectionError(host, port) from e
        logging.info("Successfully created connection to Valkey database.")
        return connection
