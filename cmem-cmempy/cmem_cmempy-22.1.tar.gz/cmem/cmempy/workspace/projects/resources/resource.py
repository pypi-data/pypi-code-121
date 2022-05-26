"""API methods for working with single resources."""
import json

import requests

from cmem.cmempy import config
from cmem.cmempy.api import (
    request,
    send_request
)


def get_resource_uri():
    """Get endpoint URI pattern for a resource."""
    path = "/workspace/projects/{}/resources/{}"
    return config.get_di_api_endpoint() + path


def get_metadata_uri():
    """Get metadata endpoint URI pattern for a resource."""
    path = "/workspace/projects/{}/resources/{}/metadata"
    return config.get_di_api_endpoint() + path


def get_resource(project_name, resource_name):
    """GET resource.

    Args:
        project_name (str): The project ID in the workspace.
        resource_name (str): The resource ID/name in the workspace.

    Returns:
        requests.Response object
    """
    response = send_request(
        get_resource_uri().format(project_name, resource_name),
        method="GET"
    )
    return response


def resource_exist(project_name, resource_name):
    """Check if a resource exist.

    A return value of true means the resource exists. A return value of true
    means the resource does not exists.

    Args:
        project_name (str): The project ID in the workspace.
        resource_name (str): The resource ID/name in the workspace.

    Returns:
        bool
    """
    try:
        get_resource_metadata(project_name, resource_name)
        return True
    except requests.exceptions.HTTPError as error:
        if error.response.status_code == 404:
            return False
        raise error


def get_resource_response(project_name, resource_name):
    """GET resource as streamable request response.

    Args:
        project_name (str): The project ID in the workspace.
        resource_name (str): The resource ID/name in the workspace.

    Returns:
        requests.Response object
    """
    resource_url = get_resource_uri().format(project_name, resource_name)
    return request(
        resource_url,
        method="GET",
        stream=True
    )


def make_new_resource(project_name, resource_name, data=None, files=None):
    """PUT create new resource.

    Args:
        project_name (str): The project ID in the workspace.
        resource_name (str): The resource ID/name in the workspace.
        data (dict): Dictionary (see requests.request) for the body
        files (dict): Dictionary (see requests.request) for multipart upload
    """
    send_request(
        get_resource_uri().format(project_name, resource_name),
        method="PUT",
        data=data,
        files=files
    )


def create_resource(
        project_name,
        resource_name,
        file_resource=None,
        replace=False
):
    """Create a new resource (streamed).

    Args:
        project_name (str): The project ID in the workspace.
        resource_name (str): The resource ID/name in the workspace.
        file_resource (file stream): Already opened byte file stream
        replace (bool): Replace resource if needed.

    Returns:
        requests.Response object

    Raises:
        ValueError: missing parameter
        ValueError: Resource exist and no replace enabled
    """
    if not file_resource:
        raise ValueError("Parameter file_name is needed.")
    if not replace and resource_exist(project_name, resource_name):
        raise ValueError(
            "Resource {} already exists in project {}."
            .format(resource_name, project_name)
        )
    # https://requests.readthedocs.io/en/latest/user/advanced/#streaming-uploads
    with file_resource as file:
        response = request(
            get_resource_uri().format(project_name, resource_name),
            method="PUT",
            stream=True,
            data=file,
        )
    return response


def delete_resource(project_name, resource_name):
    """DELETE remove existing resource.

    Args:
        project_name (str): The project ID in the workspace.
        resource_name (str): The resource ID/name in the workspace.
    """
    send_request(
        get_resource_uri().format(project_name, resource_name),
        method="DELETE"
    )


def get_resource_metadata(project_name, resource_name):
    """GET retrieve resource metadata.

    Args:
        project_name (str): The project ID in the workspace.
        resource_name (str): The resource ID/name in the workspace.

    Returns:
        Depends on what json.loads gives back
    """
    response = send_request(
        get_metadata_uri().format(project_name, resource_name),
        method="GET"
    )
    return json.loads(response.decode("utf-8"))


def get_resource_usage_data(project_name, resource_name):
    """GET retrieve the usage data of a resource.

    Args:
        project_name (str): The project ID in the workspace.
        resource_name (str): The resource ID/name in the workspace.

    Returns:
        Depends on what json.loads gives back
    """
    response = send_request(
        get_resource_uri().format(project_name, resource_name) + "/usage",
        method="GET"
    )
    return json.loads(response.decode("utf-8"))
