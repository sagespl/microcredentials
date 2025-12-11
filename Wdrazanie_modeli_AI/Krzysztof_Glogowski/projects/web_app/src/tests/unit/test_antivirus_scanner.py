import pytest

from web_app.antivirus.clamav.connector import ClamavConnector
from web_app.antivirus.clamav.scanner import AntivirusScanner
from tests.fixture import (
    ClamdNetworkSocketStub,
    fake_antivirus_socket_for_malformed_files,
    fake_antivirus_socket_for_non_malformed_files,
)

# to prevent IDE from removing unused imports START
fake_antivirus_socket_for_non_malformed_files
fake_antivirus_socket_for_malformed_files
# to prevent IDE from removing unused imports END


def test_scan_non_malformed_file(mocker, fake_antivirus_socket_for_non_malformed_files):
    # given
    mocker.patch.object(
        ClamavConnector,
        "_create_socket",
        return_value=fake_antivirus_socket_for_non_malformed_files,
    )
    scanner = AntivirusScanner(connector=ClamavConnector())
    file_content = b"1234"

    clamav_socket_spy = mocker.spy(ClamdNetworkSocketStub, "instream")

    # when
    scanner.scan(file_content)

    # then
    assert clamav_socket_spy.call_count == 1
    assert clamav_socket_spy.call_args.args[1].getvalue() == file_content


def test_scan_malformed_file(mocker, fake_antivirus_socket_for_malformed_files):
    # given
    mocker.patch.object(
        ClamavConnector,
        "_create_socket",
        return_value=fake_antivirus_socket_for_malformed_files,
    )
    scanner = AntivirusScanner(connector=ClamavConnector())
    file_content = b"1234"

    clamav_socket_spy = mocker.spy(ClamdNetworkSocketStub, "instream")

    # when # then
    with pytest.raises(ValueError, match="Virus detected: Eicar-Test-Signature"):
        scanner.scan(file_content)

    assert clamav_socket_spy.call_count == 1
    assert clamav_socket_spy.call_args.args[1].getvalue() == file_content
