from .agent import Agent
from ..base.logger import functionlogger
from ..base.typing import JsonType

import logging


__all__ = [
    "get_operations",
    "get_workflows",
    "delete_workflow"
]


@functionlogger
def get_workflows(agent: Agent, **kwds) -> JsonType:
    """
    Gets the workflows available to the user.

    Parameters
    ----------
    agent : pycarta.api.Agent
        The agent that handles communication with the Carta server.

    Returns
    -------
    dict
        JSON-formatted information about the workflows that are available
        to the user.
    """
    response = agent.get("workflow", **kwds)
    if response:
        return response.json()
    else:
        logging.debug(
            "%s API request failed with error status code %d.",
            __name__,
            response.status_code
        )
        return None


@functionlogger
def get_operations(
    agent: Agent,
    *,
    name=None,
    id=None,
    **kwds
) -> JsonType:
    """
    Gets the operations associated with a specific workflow.

    Either `name` or `id` must be specified. If both are given, then `id`
    takes precedence.

    There may be a significant performance difference when operations are
    requested for a Workflow by name. This initiates a call to get all
    workflows. The operations for the first Workflow matching `name` that
    has a valid `id` is returned.

    Parameters
    ----------
    agent : pytest.api.Agent
        The agent that handles communication with the Carta server.
    name : str
        The name of a Workflow. Either `name` or `id` must be specified.
    id : str
        The ID of a Workflow. Either `name` or `id` must be specified.

    Returns
    -------
    dict
        JSON-formatted information about the Operations the compose
        the Workflow identified by name/id. If no such
    """
    def _get_operations_from_workflow_by_id(uid):
        if uid:
            response = agent.get("workflow/{}/operations".format(uid), **kwds)
            if response:
                return response.json()
            else:
                logging.debug(
                    "%s API request failed with error status code %d.",
                    __name__,
                    response.status_code
                )
                return None
        else:
            return None

    def _get_operations_from_workflow_by_name(name):
        if name:
            for w in get_workflows(agent, **kwds):
                if w["name"] == name and "id" in w:
                    return w["operations"]
            return None
        else:
            return None

    return (_get_operations_from_workflow_by_id(id) or
            _get_operations_from_workflow_by_name(name))


@functionlogger
def delete_workflow(
    agent: Agent,
    *,
    name=None,
    id=None,
    **kwds
) -> JsonType:
    """
    Deletes the Workflow that matches the specified name/id.

    Either `name` or `id` must be specified. If both are given, then `id`
    takes precedence.

    There may be a significant performance difference when operations are
    requested for a Workflow by name. This initiates a call to get all
    workflows. The operations for the first Workflow matching `name` that
    has a valid `id` is deleted.

    Parameters
    ----------
    agent : pytest.api.Agent
        The agent that handles communication with the Carta server.
    name : str
        The name of a Workflow. Either `name` or `id` must be specified.
    id : str
        The ID of a Workflow. Either `name` or `id` must be specified.

    Returns
    -------
    dict
        JSON-formatted information about the Operations the compose
        the Workflow identified by name/id. If no such
    """
    def _delete_operations_from_workflow_by_id(uid):
        if uid:
            response = agent.delete("workflow/{}/operations".format(uid), **kwds)
            return bool(response)
            if response:
                return bool(response)
            else:
                logging.debug(
                    "%s API request failed with error status code %d.",
                    __name__,
                    response.status_code
                )
                return False
        else:
            return False

    def _delete_operations_from_workflow_by_name(name):
        if name:
            for w in get_workflows(agent, **kwds):
                if w["name"] == name and "id" in w:
                    return _delete_operations_from_workflow_by_id(w["id"])
        else:
            return False

    return (_get_operations_from_workflow_by_id(id) or
            _get_operations_from_workflow_by_name(name))
