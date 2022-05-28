import argparse
import json
import os
import tempfile
import time
import typing
from collections.abc import Mapping

import mlflow
import numpy as np

from mlfoundry import constants, env_vars
from mlfoundry.exceptions import MlflowException, MlFoundryException


def resolve_tracking_uri(tracking_uri: typing.Optional[str]):
    return (
        tracking_uri
        or os.getenv(env_vars.TRACKING_HOST)
        or constants.DEFAULT_TRACKING_URI
    )


class NumpyEncoder(json.JSONEncoder):
    """Special json encoder for numpy types"""

    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


ParamsType = typing.Union[typing.Mapping[str, typing.Any], argparse.Namespace]


def process_params(params: ParamsType) -> typing.Dict[str, typing.Any]:
    if isinstance(params, Mapping):
        return params
    if isinstance(params, argparse.Namespace):
        return vars(params)
    # TODO: add absl support if required
    # move to a different file then
    raise MlFoundryException(
        "params should be either argparse.Namespace or a Mapping (dict) type"
    )


def log_artifact_blob(
    mlflow_client: mlflow.tracking.MlflowClient,
    run_id: str,
    blob: typing.Union[str, bytes],
    file_name: str,
    artifact_path: typing.Optional[str] = None,
):
    with tempfile.TemporaryDirectory(prefix=run_id) as tmpdirname:
        local_path = os.path.join(tmpdirname, file_name)
        mode = "wb" if isinstance(blob, bytes) else "w"
        with open(local_path, mode) as local_file:
            local_file.write(blob)
        mlflow_client.log_artifact(run_id, local_path, artifact_path=artifact_path)


def mapping_to_mlflow_metric(
    metrics: typing.Mapping[str, float],
    timestamp: typing.Optional[int] = None,
    step: int = 0,
) -> typing.Dict[str, mlflow.entities.Metric]:
    if timestamp is None:
        timestamp = int(time.time() * 1000)
    mlflow_metrics = {
        key: mlflow.entities.Metric(key, value, timestamp, step=step)
        for key, value in metrics.items()
    }
    return mlflow_metrics
