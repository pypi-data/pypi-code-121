"""API for working with a single project activity."""
import json

from cmem.cmempy import config
from cmem.cmempy.api import send_request


def get_activity_uri():
    """Get endpoint URI pattern for a activity."""
    path = "/workspace/projects/{}/activities/{}"
    return config.get_di_api_endpoint() + path


def get_start_activity_uri():
    """Get start endpoint URI pattern for a activity."""
    return get_activity_uri() + "/start"


def get_start_blocking_activity_uri():
    """Get start-blocking endpoint URI pattern for a activity."""
    return get_activity_uri() + "/startBlocking"


def get_cancel_activity_uri():
    """Get cancel endpoint URI pattern for a activity."""
    return get_activity_uri() + "/cancel"


def get_config_activity_uri():
    """Get config endpoint URI pattern for a activity."""
    return get_activity_uri() + "/config"


def get_status_activity_uri():
    """Get status endpoint URI pattern for a activity."""
    return get_activity_uri() + "/status"


def get_value_activity_uri():
    """Get value endpoint URI pattern for a activity."""
    return get_activity_uri() + "/value"


def start_project_activity(project_name,
                           activity_name,
                           blocking=False,
                           data=None):
    """POST start activity."""
    if blocking:
        return start_blocking_project_activity(
            project_name,
            activity_name,
            data
        )
    return send_request(
        get_start_activity_uri().format(
            project_name,
            activity_name
        ),
        method="POST",
        data=data
    ).decode("utf-8")


def get_project_activity_status(project_name, activity_name):
    """GET project activity status."""
    return json.loads(send_request(
        get_status_activity_uri().format(
            project_name,
            activity_name
        ),
        method="GET"
    ).decode("utf-8"))


def cancel_project_activity(project_name, activity_name):
    """Cancel project activity."""
    return send_request(
        get_cancel_activity_uri().format(
            project_name,
            activity_name
        ),
        method="POST"
    ).decode("utf-8")


def start_blocking_project_activity(project_name, activity_name, data):
    """POST start blocking activity."""
    return send_request(
        get_start_blocking_activity_uri().format(
            project_name,
            activity_name
        ),
        method="POST",
        data=data
    ).decode("utf-8")
