import json

from tests.fixture import fake_valkey
from web_app.database.valkey.client import ValkeyClient
from web_app.database.valkey.connector import ValkeyConnector


def test_read_when_key_exists(mocker, fake_valkey):
    # given
    mocker.patch.object(ValkeyConnector, "_create_connection", return_value=fake_valkey)
    connector = ValkeyConnector("0.0.0.0", 0)
    valkey_client = ValkeyClient(connector)
    key = "test_key"
    value = [{"label": 0, "confidence": 0.96}]
    fake_valkey.set(key, json.dumps(value))

    # when
    result = valkey_client.read(key)

    # then
    assert result == value


def test_read_when_key_not_exists(mocker, fake_valkey):
    # given
    mocker.patch.object(ValkeyConnector, "_create_connection", return_value=fake_valkey)
    connector = ValkeyConnector("0.0.0.0", 0)
    valkey_client = ValkeyClient(connector)
    key = "non_existent_key"

    # when
    result = valkey_client.read(key)

    # then
    assert result is None


def test_write(mocker, fake_valkey):
    # given
    mocker.patch.object(ValkeyConnector, "_create_connection", return_value=fake_valkey)
    connector = ValkeyConnector("0.0.0.0", 0)
    valkey_client = ValkeyClient(connector)
    key = "test_key"
    value = [{"label": 0, "confidence": 0.96}]

    # when
    before_write = valkey_client.read(key)
    valkey_client.write(key, value)
    after_write = valkey_client.read(key)

    # then
    assert before_write is None
    assert after_write == value
