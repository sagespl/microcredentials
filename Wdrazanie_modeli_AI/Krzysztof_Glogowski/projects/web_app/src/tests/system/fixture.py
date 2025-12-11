import logging
import subprocess
import time

import pytest
import requests
import torch

from tests.fixture import ClassifierStub


@pytest.fixture(scope="session")
def request_endpoint_v1():
    return "http://localhost:8080/v1/predict"


@pytest.fixture(scope="session")
def request_endpoint_v2():
    return "http://localhost:8080/v2/predict"


@pytest.fixture(scope="session")
def docker():
    build_test_model()
    startup_docker()

    yield

    stop_docker()


def build_test_model():
    test_model = ClassifierStub()
    test_model.eval()
    scripted_model = torch.jit.script(test_model)
    scripted_model.save("resources/test_model.pt")


def startup_docker():
    try:
        logging.info("==> Starting Docker Compose")
        subprocess.run(
            [
                "docker",
                "compose",
                "-f",
                "../deploy/docker/docker-compose.yaml",
                "--env-file",
                "../deploy/docker/test.env",
                "up",
                "--build",
                "-d",
            ],
            check=True,
        )

        wait_for_http_service("http://localhost:8080/health")

    except Exception as e:
        logging.error(f"Failed to start Docker Compose: {e}")
        stop_docker()
        raise


def wait_for_http_service(url, timeout=60, interval=1):
    start = time.time()
    while time.time() - start < timeout:
        try:
            response = requests.get(url)
            if 200 <= response.status_code < 300:
                logging.info(f"✅ Service at {url} is healthy (HTTP {response.status_code})")
                return True
            else:
                logging.info(f"⏳ Service not ready (HTTP {response.status_code})")
        except requests.RequestException as e:
            logging.info(f"⏳ Waiting for service at {url}... ({e})")
        time.sleep(interval)
    raise TimeoutError(f"❌ Timeout: service at {url} did not become healthy in {timeout} seconds")


def stop_docker():
    try:
        logging.info("==> Stopping Docker Compose")
        subprocess.run(
            ["docker", "compose", "-f", "../deploy/docker/docker-compose.yaml", "down"], check=True
        )
    except Exception as e:
        logging.error(f"Failed to stop Docker Compose: {e}")
