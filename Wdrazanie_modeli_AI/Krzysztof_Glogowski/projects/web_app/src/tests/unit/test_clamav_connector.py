import clamd
import pytest
from clamd import ClamdNetworkSocket

from web_app.antivirus.clamav.connector import ClamavConnector
from web_app.utils.error import ClamavConnectionError, ClamavConnectionNotAliveError
from tests.fixture import fake_antivirus_socket_for_non_malformed_files

# to prevent IDE from removing unused imports START
fake_antivirus_socket_for_non_malformed_files
# to prevent IDE from removing unused imports END


def test_create_connection(fake_antivirus_socket_for_non_malformed_files, mocker):
    # given
    mocker.patch(
        "web_app.antivirus.clamav.connector.clamd.ClamdNetworkSocket",
        return_value=fake_antivirus_socket_for_non_malformed_files,
    )
    ping_spy = mocker.spy(fake_antivirus_socket_for_non_malformed_files, "ping")
    # when
    socket = ClamavConnector._create_socket("0.0.0.0", 0)

    # then
    assert socket is not None
    assert type(socket) is fake_antivirus_socket_for_non_malformed_files.__class__
    assert ping_spy.call_count == 1


def test_create_connection_exception(mocker):
    # given
    ping_spy = mocker.spy(ClamdNetworkSocket, "ping")

    # when # then
    with pytest.raises(ClamavConnectionError):
        ClamavConnector._create_socket("0.0.0.0", 0)

    assert ping_spy.call_count == 1


def test_is_alive(fake_antivirus_socket_for_non_malformed_files, mocker):
    # given
    mocker.patch(
        "web_app.antivirus.clamav.connector.clamd.ClamdNetworkSocket",
        return_value=fake_antivirus_socket_for_non_malformed_files,
    )
    ping_spy = mocker.spy(fake_antivirus_socket_for_non_malformed_files, "ping")
    connector = ClamavConnector("0.0.0.0", 0)

    # when
    connector.is_alive()

    # then
    assert ping_spy.call_count == 2


def test_is_alive_exception(mocker):
    # given
    mocker.patch(
        "web_app.antivirus.clamav.connector.clamd.ClamdNetworkSocket.ping",
        side_effect=[None, clamd.ConnectionError()],
    )
    ping_spy = mocker.spy(ClamdNetworkSocket, "ping")
    connector = ClamavConnector("0.0.0.0", 0)

    # when # then
    with pytest.raises(ClamavConnectionNotAliveError):
        connector.is_alive()

    assert ping_spy.call_count == 2
