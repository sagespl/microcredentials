import os

import pytest


@pytest.fixture(scope="session", autouse=True)
def test_directory():
    os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "web_app")))
