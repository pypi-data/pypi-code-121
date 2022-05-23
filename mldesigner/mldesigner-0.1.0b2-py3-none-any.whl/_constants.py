# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from enum import Enum

BASE_PATH_CONTEXT_KEY = "base_path"
VALID_NAME_CHARS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._-")
MLDESIGNER_COMPONENT_EXECUTION = "MLDESIGNER_COMPONENT_EXECUTION"
MLDESIGNER_COMPONENT_EXECUTOR_MODULE = "mldesigner.executor"


class NodeType(object):
    COMMAND = "command"
    SWEEP = "sweep"
    PARALLEL = "parallel"
    AUTOML = "automl"


class DefaultEnv:
    CONDA_FILE = {
        "name": "default_environment",
        "channels": ["defaults"],
        "dependencies": [
            "python=3.8.12",
            "pip=21.2.2",
            {
                "pip": [
                    "--extra-index-url=https://azuremlsdktestpypi.azureedge.net/sdk-cli-v2",
                    "mldesigner==0.0.62745813",
                ]
            },
        ],
    }
    IMAGE = "mcr.microsoft.com/azureml/openmpi3.1.2-ubuntu18.04"


class ComponentSource(Enum):
    """Indicate where the component is constructed."""

    BUILDER = "BUILDER"
    MLDESIGNER = "MLDESIGNER"
    OTHER = "OTHER"
    REST = "REST"
    YAML = "YAML"
