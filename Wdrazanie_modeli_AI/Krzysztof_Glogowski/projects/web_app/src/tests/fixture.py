from io import BytesIO

import fakeredis
import fsspec
import pytest
import torch
from torch import nn


class ClamdNetworkSocketStub:
    def __init__(self, return_malformed: bool = False, *args, **kwargs):
        self.return_malformed = return_malformed

    def ping(self):
        pass

    def instream(self, buff):
        return (
            {"stream": ("FOUND", "Eicar-Test-Signature")}
            if self.return_malformed
            else {"stream": ("OK", None)}
        )


class ClassifierStub(nn.Module):
    def __init__(self):
        super().__init__()

    def forward(self, x, l):  # noqa: E741
        return torch.tensor([0.1, 0.6, 0.9, -0.01])

    @torch.jit.export
    def predict_proba(self, x, l):  # noqa: E741
        return torch.tensor(
            [0.17330732941627502, 0.28573545813560486, 0.385702520608902, 0.15525461733341217]
        )


@pytest.fixture(scope="session")
def one_page_document_content():
    with open("../tests/resources/test.pdf", "rb") as file:
        file_content = file.read()

    return file_content


@pytest.fixture(scope="session")
def two_pages_document_content():
    with open("../tests/resources/test_2_pages.pdf", "rb") as file:
        file_content = file.read()

    return file_content


@pytest.fixture(scope="session")
def fake_script_model():
    model = ClassifierStub()
    script_module = torch.jit.script(model)
    return script_module


@pytest.fixture(scope="session")
def model_in_in_memory_filesystem(fake_script_model):
    buffer = BytesIO()
    torch.jit.save(fake_script_model, buffer)
    buffer.seek(0)
    fs = fsspec.filesystem("memory")
    with fs.open("memory://model.pt", "wb") as f:
        f.write(buffer.read())


@pytest.fixture(scope="session")
def model_prediction_v1():
    return {"label": 2}


@pytest.fixture(scope="session")
def model_prediction_v2():
    return [
        {"confidence": 0.385702520608902, "label": 2},
        {"confidence": 0.28573545813560486, "label": 1},
        {"confidence": 0.17330732941627502, "label": 0},
        {"confidence": 0.15525461733341217, "label": 3},
    ]


@pytest.fixture(scope="session")
def request_body(one_page_document_content):
    return {"document": ("test.pdf", one_page_document_content, "application/pdf")}


@pytest.fixture(scope="session")
def invalid_request_body():
    return {"document": ("test.pdf", bytes(10 * 1024 * 1024 + 10), "application/pdf")}


@pytest.fixture(scope="session")
def request_headers():
    return {
        "Content-Length": "4318",
        "Content-Type": "multipart/form-data; boundary=----WebKitFormBoundaryovh3ZI9xJeH2sx4q",
    }


@pytest.fixture(scope="function")
def fake_antivirus_socket_for_non_malformed_files():
    return ClamdNetworkSocketStub()


@pytest.fixture(scope="function")
def fake_antivirus_socket_for_malformed_files():
    return ClamdNetworkSocketStub(return_malformed=True)


@pytest.fixture(scope="function")
def fake_valkey():
    return fakeredis.FakeRedis()
