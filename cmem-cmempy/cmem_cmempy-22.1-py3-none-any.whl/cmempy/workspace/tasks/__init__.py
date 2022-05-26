"""API for getting tasks in the data integration workspace."""

import json

from cmem.cmempy import config
from cmem.cmempy.api import send_request


def get_task_uri():
    """Get endpoint URL for the tasks API."""
    path = "/workspace/projects/{}/tasks/{}"
    return config.get_di_api_endpoint() + path


def get_task(
        project=None,
        task=None,
        with_labels=True
):
    """GET a task description."""
    response = send_request(
        get_task_uri().format(
            project,
            task
        ) + "?withLabels=" + str(with_labels).lower(),
        method="GET",
        headers={'Accept': 'application/json'},
    )
    return json.loads(response.decode("utf-8"))


def delete_task(
        project=None,
        task=None
):
    """DELETE a task."""
    send_request(
        get_task_uri().format(
            project,
            task
        ),
        method="DELETE"
    )


def patch_parameter(
        project=None,
        task=None,
        data=None
):
    """PATCH a task."""
    headers = {'Content-Type': 'application/json'}
    data = json.dumps(data)
    send_request(
        get_task_uri().format(
            project,
            task
        ),
        data=data,
        headers=headers,
        method="PATCH"
    )
