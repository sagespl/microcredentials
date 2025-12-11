import random

import fsspec
import gevent
import pandas as pd
from locust import task, FastHttpUser, constant, between, events
from locust.argument_parser import LocustArgumentParser


@events.init_command_line_parser.add_listener
def _(parser: LocustArgumentParser):
    parser.add_argument(
        "--metadata_path",
        type=str,
        env_var="METADATA_PATH",
        default="projects/web_app/src/tests/resources/load_test/metadata.csv",
        help="Path to metadata file",
    )


class BusinessUser(FastHttpUser):
    abstract = True
    time_accept_in_seconds = 5

    def on_start(self):
        metadata_path = self.environment.parsed_options.metadata_path
        test_data = pd.read_csv(metadata_path)
        self.document_paths = test_data["path"].tolist()

    @property
    def request_body(self):
        file_path = random.choice(self.document_paths)
        with fsspec.open(file_path, "rb") as f:
            file_content = f.read()
        return {"document": (file_path.split("/")[-1], file_content, "application/pdf")}


class HumanUser(BusinessUser):
    wait_time = between(1, 20)

    @task
    def classify_document_v1(self):
        self.client.get("/")
        gevent.sleep(random.uniform(1, 5))
        self.client.post("/v1/predict", files=self.request_body)

    @task
    def classify_document_v2(self):
        self.client.get("/")
        gevent.sleep(random.uniform(1, 5))
        self.client.post("/v2/predict", files=self.request_body)


class ServiceUser(BusinessUser):
    @task
    def classify_document_v1(self):
        self.client.post("/v1/predict", files=self.request_body)

    @task
    def classify_document_v2(self):
        self.client.post("/v2/predict", files=self.request_body)


class KubernetesUser(FastHttpUser):
    wait_time = constant(10)

    @task
    def health_check(self):
        self.client.get("/health")
        gevent.sleep(random.uniform(0, 0.3))
        self.client.get("/readiness")
