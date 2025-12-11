import logging

from web_app.database.valkey.client import ValkeyClient


def write_to_valkey(valkey_client: ValkeyClient, key: str, value: int):
    logging.info(f"Started background task to write to Valkey for {key=} and {value=}")
    valkey_client.write(key, value)
    logging.info("Successfully ended background task to write to Valkey.")
