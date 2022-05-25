import hyperthought as ht
from .base import Template, Workspace, HyperThoughtKeyFinder
from .parsers import from_json
from typing import Dict, Union


__all__ = ["get_children", "get_templates", "get_workspaces"]


def get_children(auth: ht.auth.Authorization, parent: Union[str, ht.api.workflow.Workflow]):
    """
    Gets the list of children from a Workflow.

    Parameters
    ----------
    auth : hyperthought.auth.Authorization
        Authorized agent to handle communication with the HyperThought API.
    parent : str or hyperthought.api.workflow.Workflow
        Primary key identifier of the parent workflow. This may be a UUID or path,
        or the hyperthought.api.workflow.Workflow object itself.

    Returns
    -------
    list[hyperthought.api.workflow.Workflow]
        The Elements/Children of the parent Workflow.
    """
    if isinstance(parent, ht.api.workflow.Workflow):
        return parent.children
    else:
        api = ht.api.workflow.WorkflowAPI(auth)
        return [
            from_json(child)
            for child in api.get_children(HyperThoughtKeyFinder(auth)(parent))
        ]


def get_templates(auth: ht.auth.Authorization, pk: Union[str, Workspace]):
    """
    Returns a mapping of Templates to their names and ids.

    Parameters
    ----------
    auth : hyperthought.auth.Authorization
        Authorized agent to handle communication with the HyperThought API.
    pk : str or pycarta.interface.hyperthought.base.Workspace
        Primary key identifier of the workspace. This may be a UUID or path,
        or the hyperthought.api.workflow.Workspace object itself.

    Returns
    -------
    dict[str, pycarta.interface.hyperthought.base.Template]
        The resulting dictionary keys the Template to its ID and to its name.
    """
    agent = ht.api.workflow.WorkflowAPI(auth)
    key_finder = HyperThoughtKeyFinder(auth)
    templates = [Template(t) for t in agent.get_templates(key_finder(pk))]
    return {
        **{t.id: t for t in templates},
        **{t["name"]: t for t in templates}
    }


def get_workspaces(auth: ht.auth.Authorization) -> Dict[str, Workspace]:
    """
    Returns a mapping of Workspaces to their names and ids.

    Parameters
    ----------
    auth : hyperthought.auth.Authorization
        Authorized agent to handle communication with the HyperThought API.

    Returns
    -------
    dict[str, pycarta.interface.hyperthought.base.Workspace]
        The resulting dictionary keys the Workspace to its ID and to its name.
    """
    agent = ht.api.workspaces.WorkspacesAPI(auth)
    ws = [Workspace(w) for w in agent.get_workspaces()]
    return {
        **{w.id: w for w in ws},
        **{w["name"]: w for w in ws}
    }
