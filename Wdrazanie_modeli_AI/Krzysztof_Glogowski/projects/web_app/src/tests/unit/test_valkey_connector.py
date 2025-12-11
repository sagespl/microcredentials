import pytest
import valkey

from web_app.database.valkey.connector import ValkeyConnector
from web_app.utils.error import ValkeyConnectionError, ValkeyConnectionNotAliveError
from tests.fixture import fake_valkey


def test_create_connection(mocker, fake_valkey):
    # given
    mocker.patch("web_app.database.valkey.connector.valkey.Valkey", return_value=fake_valkey)
    ping_spy = mocker.spy(fake_valkey, "ping")

    # when
    connector = ValkeyConnector._create_connection("0.0.0.0", 0)

    # then
    assert connector is not None
    assert type(connector) is fake_valkey.__class__
    assert ping_spy.call_count == 1


def test_create_connection_exception(mocker):
    # given
    ping_spy = mocker.spy(valkey.Valkey, "ping")

    # when # then
    with pytest.raises(ValkeyConnectionError):
        ValkeyConnector._create_connection("0.0.0.0", 0)

    assert ping_spy.call_count == 1


def test_is_alive(fake_valkey, mocker):
    # given
    mocker.patch("web_app.database.valkey.connector.valkey.Valkey", return_value=fake_valkey)
    ping_spy = mocker.spy(fake_valkey, "ping")
    connector = ValkeyConnector("0.0.0.0", 0)

    # when
    connector.is_alive()

    # then
    assert ping_spy.call_count == 2


def test_is_alive_exception(mocker):
    # given
    mocker.patch(
        "web_app.database.valkey.connector.valkey.Valkey.ping",
        side_effect=[None, valkey.exceptions.ConnectionError()],
    )
    ping_spy = mocker.spy(valkey.Valkey, "ping")
    connector = ValkeyConnector("0.0.0.0", 0)

    # when # then
    with pytest.raises(ValkeyConnectionNotAliveError):
        connector.is_alive()

    assert ping_spy.call_count == 2


def test_close(fake_valkey, mocker):
    # given
    mocker.patch("web_app.database.valkey.connector.valkey.Valkey", return_value=fake_valkey)
    connector = ValkeyConnector("0.0.0.0", 0)
    disconnect_spy = mocker.spy(fake_valkey.connection_pool, "disconnect")

    # when
    connector.close()

    # then
    assert disconnect_spy.call_count == 1
    assert disconnect_spy.call_args.kwargs["inuse_connections"] is True
