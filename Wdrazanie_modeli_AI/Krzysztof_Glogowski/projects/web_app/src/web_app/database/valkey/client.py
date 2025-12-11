import json
import logging

from web_app.database.valkey.connector import ValkeyConnector


class ValkeyClient:
    def __init__(self, connector: ValkeyConnector):
        self.connector = connector

    def read(self, key: str) -> list[dict[str, int | float]] | None:
        logging.info("Getting response from Valkey")
        self.connector.is_alive()
        raw_value = self.connector.connection.get(key)
        if raw_value is not None:
            value = json.loads(raw_value)  # type: ignore
            logging.info("Returning response from Valkey")
            return value
        else:
            logging.info("Response not available in Valkey")
            return None

    def write(self, key: str, value: list[dict[str, int | float]]) -> None:
        logging.info("Saving data to Valkey")
        self.connector.is_alive()
        value_to_save = json.dumps(value)
        self.connector.connection.set(key, value_to_save)
        logging.info("Successfully saved data in Valkey")
