"""API methods for working with single datasets."""
import json

from cmem.cmempy import config
from cmem.cmempy.api import send_request


def get_dataset_uri():
    """Get endpoint URI pattern for a dataset."""
    path = "/workspace/projects/{}/datasets/{}"
    return config.get_di_api_endpoint() + path


def get_dataset(project_name, dataset_name):
    """GET retrieve single dataset."""
    headers = {
        "Accept": "application/json"
    }
    response = send_request(
        get_dataset_uri().format(project_name, dataset_name),
        method="GET",
        headers=headers
    )
    return json.loads(response.decode("utf-8"))


def make_new_dataset(project_name, dataset_name,
                     dataset_type, parameters, autoconfigure):
    """PUT create new dataset (deprecated)."""
    data = {
        "id": "{}".format(dataset_name),
        "type": "{}".format(dataset_type),
        "parameters": parameters
    }
    data = json.dumps(data).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    params = None
    if autoconfigure:
        params = {"autoConfigure": "true"}
    send_request(
        get_dataset_uri().format(project_name, dataset_name),
        method="PUT",
        data=data,
        headers=headers,
        params=params
    )


def delete_dataset(project_name, dataset_name):
    """DELETE remove existing dataset."""
    send_request(
        get_dataset_uri().format(project_name, dataset_name),
        method="DELETE"
    )


def create_dataset(
        project_id, dataset_type,
        dataset_id=None, parameter=None, metadata=None
):
    """Create a dataset.

    In difference to make_new_dataset, this uses the task API and does
    not enforce an ID in advance. Also it allows for metadata parameters.
    """
    if parameter is None:
        parameter = {}
    if metadata is None:
        metadata = {}
    # add needed base task data
    data = {
        "taskType": "Dataset",
        "type": dataset_type,
        "parameters": parameter,
        "metadata": metadata
    }
    # add the optional task / dataset ID
    if dataset_id:
        data["id"] = dataset_id
    params = None
    path = "/workspace/projects/{}/tasks".format(project_id)
    return send_request(
        config.get_di_api_endpoint() + path,
        method="POST",
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        params=params
    )
