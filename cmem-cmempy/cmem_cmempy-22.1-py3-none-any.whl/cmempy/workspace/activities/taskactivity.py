"""API for working with task activities."""
import json

from cmem.cmempy import config
from cmem.cmempy.api import send_request
from cmem.cmempy.workspace.activities import (
    ACTIVITY_TYPE_EXECUTE_DEFAULTWORKFLOW
)


def get_activity_uri():
    """Get endpoint URI pattern for an activity."""
    path = "/workspace/projects/{}/tasks/{}/activities/{}"
    return config.get_di_api_endpoint() + path


def get_start_activity_uri():
    """Get start endpoint URI pattern for an activity."""
    return get_activity_uri() + "/start"


def get_start_blocking_activity_uri():
    """Get start-blocking endpoint URI pattern for an activity."""
    return get_activity_uri() + "/startBlocking"


def get_config_activity_uri():
    """Get config endpoint URI pattern for an activity."""
    return get_activity_uri() + "/config"


def get_status_activity_uri():
    """Get status endpoint URI pattern for an activity."""
    return get_activity_uri() + "/status"


def get_value_activity_uri():
    """Get value endpoint URI pattern for an activity."""
    return get_activity_uri() + "/value"


def start_task_activity(project_name,
                        task_name,
                        activity_name=ACTIVITY_TYPE_EXECUTE_DEFAULTWORKFLOW,
                        blocking=False,
                        data=None):
    """POST start task activity."""
    if blocking:
        return start_blocking_task_activity(
            project_name,
            task_name,
            activity_name=activity_name,
            data=data
        )
    return send_request(
        get_start_activity_uri().format(
            project_name,
            task_name,
            activity_name
        ),
        method="POST",
        data=data
    ).decode("utf-8")


def start_blocking_task_activity(
        project_name,
        task_name,
        activity_name=ACTIVITY_TYPE_EXECUTE_DEFAULTWORKFLOW,
        data=None
):
    """POST start blocking task activity."""
    return send_request(
        get_start_blocking_activity_uri().format(
            project_name,
            task_name,
            activity_name
        ),
        method="POST",
        data=data
    ).decode("utf-8")


def get_activity_status(
        project_name,
        task_name,
        activity_name=ACTIVITY_TYPE_EXECUTE_DEFAULTWORKFLOW):
    """GET retrieve activity status."""
    return json.loads(send_request(
        get_status_activity_uri().format(
            project_name,
            task_name,
            activity_name
        ),
        method="GET"
    ).decode("utf-8"))
