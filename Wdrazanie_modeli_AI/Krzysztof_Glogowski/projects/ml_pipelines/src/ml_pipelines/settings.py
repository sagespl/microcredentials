"""Project settings.

There is no need to edit this file
unless you want to change values from the Kedro defaults.
For further information, including these default values, see
https://docs.kedro.org/en/stable/kedro_project_setup/settings.html.
"""
import sys


from kedro.config import OmegaConfigLoader

from hooks import SeedHook, PerformanceReportHook, MlFlowHook

HOOKS = (SeedHook(), PerformanceReportHook(), MlFlowHook())
CONF_SOURCE = "projects/ml_pipelines/conf"
CONFIG_LOADER_CLASS = OmegaConfigLoader
CONFIG_LOADER_ARGS = {
    "base_env": "base",
    "default_run_env": "local",
}

sys.path.append("projects/common/src")