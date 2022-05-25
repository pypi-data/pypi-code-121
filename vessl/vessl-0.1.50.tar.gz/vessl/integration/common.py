import os
from typing import Dict, List, Optional, SupportsFloat, Union

from openapi_client.models import (
    ResponseExperimentInfo,
)
from vessl import vessl_api
from vessl.experiment import read_experiment_by_id
from vessl.util.image import Image

ImageRowType = Dict[str, List[Image]]
MetricRowType = Dict[str, SupportsFloat]
RowType = Union[ImageRowType, MetricRowType]

current_experiment: Optional[ResponseExperimentInfo] = None


def _update_current_experiment():
    global current_experiment
    experiment_id = os.environ.get("VESSL_EXPERIMENT_ID", None)
    access_token = os.environ.get("VESSL_ACCESS_TOKEN", None)

    if experiment_id is None or access_token is None:
        return

    vessl_api.configure_access_token(access_token)
    current_experiment = read_experiment_by_id(int(experiment_id))


def get_current_experiment() -> Optional[ResponseExperimentInfo]:
    global current_experiment
    if current_experiment != None:
        return current_experiment

    _update_current_experiment()
    return current_experiment


def get_current_experiment_id() -> int:
    assert current_experiment
    assert current_experiment.id
    return current_experiment.id
