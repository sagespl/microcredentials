import datetime as dt
import os
import random
from time import monotonic

import flatdict
import mlflow
import numpy as np
import torch
from dotenv import load_dotenv
from kedro.framework.hooks import hook_impl
from mlflow.entities import RunStatus

from ml_pipelines.logger import logger


class SeedHook:
    def __init__(self):
        self.seed = 42

    @hook_impl
    def after_context_created(self, context):
        seed = context.params.get("seed")
        if seed is not None:
            self.seed = seed

    @hook_impl
    def before_pipeline_run(self, run_params, pipeline, catalog):
        random.seed(self.seed)
        np.random.seed(self.seed)
        torch.manual_seed(self.seed)


class PerformanceReportHook:
    def __init__(self):
        self.node_times = {}

    @hook_impl
    def before_node_run(self, node, catalog, inputs, is_async, session_id):
        self.node_times[node.name] = monotonic()

    @hook_impl
    def after_node_run(self, node, catalog, inputs, outputs, is_async, session_id):
        self.node_times[node.name] = monotonic() - self.node_times[node.name]

    @hook_impl
    def after_pipeline_run(self, run_params, run_result, pipeline, catalog):
        report = ["-" * 80, "Performance report:"]
        for node_name, time in self.node_times.items():
            report.append(f"{node_name: >50}: {time:0.4f}s")
        report.append("")
        report.append(f"{'Total time': >50}: {sum(self.node_times.values()):0.4f}s")
        report.append("-" * 80)
        logger.info("\n".join(report))


class MlFlowHook:
    def __init__(self):
        load_dotenv()

    @hook_impl
    def after_context_created(self, context):
        self.params = context.params

    @hook_impl
    def before_pipeline_run(self, run_params, pipeline, catalog):
        mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI"))
        mlflow.set_experiment(os.getenv("EXPERIMENT_NAME"))

        pipeline_name = run_params.get("pipeline_name") or "default"

        logger.info(f"pipeline name::{pipeline_name}")

        tags = {
            "pipeline": pipeline_name,
        }
        run_name = f"{dt.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
        mlflow.start_run(run_name=run_name, tags=tags, description="Documents clustering by Kedro")
        mlflow.log_params(flatdict.FlatDict(self.params, delimiter="."))

    @hook_impl
    def after_pipeline_run(self, run_params, run_result, pipeline, catalog):
        mlflow.end_run()

    @hook_impl
    def on_pipeline_error(self, error, run_params, pipeline, catalog):
        mlflow.end_run(RunStatus.to_string(RunStatus.FAILED))
