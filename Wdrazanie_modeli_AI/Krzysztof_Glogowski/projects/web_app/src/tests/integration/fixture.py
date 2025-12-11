import os

import pytest
from starlette.testclient import TestClient

from web_app.antivirus.clamav.connector import ClamavConnector
from web_app.database.valkey.connector import ValkeyConnector
from web_app.main import app


@pytest.fixture(scope="function")
def initialized_app(
    mocker,
    fake_valkey,
    fake_antivirus_socket_for_non_malformed_files,
    model_in_in_memory_filesystem,
    in_memory_model_path,
):
    mocker.patch.object(ValkeyConnector, "_create_connection", return_value=fake_valkey)
    mocker.patch.object(
        ClamavConnector,
        "_create_socket",
        return_value=fake_antivirus_socket_for_non_malformed_files,
    )
    with TestClient(app=app, raise_server_exceptions=False) as client:
        yield client


@pytest.fixture(scope="session", autouse=True)
def in_memory_model_path():
    os.environ["DYNACONF_MODEL_PATH"] = "memory://model.pt"
    yield
    # Cleanup if needed


@pytest.fixture(scope="session")
def document_hash_v1():
    return "v1_9e2e157be3cd927f16faac37bf9167b85cbdd81ea83264837e4802e04713239f"


@pytest.fixture(scope="session")
def document_hash_v2():
    return "v2_9e2e157be3cd927f16faac37bf9167b85cbdd81ea83264837e4802e04713239f"


@pytest.fixture(scope="session")
def request_endpoint_v1():
    return "/v1/predict"


@pytest.fixture(scope="session")
def request_endpoint_v2():
    return "/v2/predict"
