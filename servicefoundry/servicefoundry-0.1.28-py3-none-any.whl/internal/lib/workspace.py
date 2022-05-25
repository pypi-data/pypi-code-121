from typing import Any, Dict, Optional

from servicefoundry.internal.clients.service_foundry_client import (
    ServiceFoundryServiceClient,
)
from servicefoundry.internal.console import console
from servicefoundry.internal.lib.messages import (
    PROMPT_CREATING_NEW_WORKSPACE,
    PROMPT_REMOVING_WORKSPACE,
    PROMPT_UNSETTING_WORKSPACE_CONTEXT,
    PROMPT_USING_CLUSTER_CONTEXT,
)
from servicefoundry.internal.lib.util import (
    all_workspaces,
    resolve_cluster_or_error,
    resolve_workspace_or_error,
    resolve_workspaces,
)
from servicefoundry.internal.model.entity import Workspace


def create_workspace(
    name: str,
    cluster_name_or_id: Optional[str] = None,
    tail_logs: bool = True,
    non_interactive: bool = True,
    client: Optional[ServiceFoundryServiceClient] = None,
) -> Workspace:
    client = client or ServiceFoundryServiceClient.get_client()
    cluster = resolve_cluster_or_error(
        name_or_id=cluster_name_or_id, non_interactive=non_interactive, client=client
    )
    console.print(PROMPT_USING_CLUSTER_CONTEXT.format(cluster.name))
    with console.status(PROMPT_CREATING_NEW_WORKSPACE.format(name), spinner="dots"):
        response = client.create_workspace(cluster_id=cluster.id, name=name)
        workspace = Workspace.from_dict(response["workspace"])
        if tail_logs:
            client.tail_logs(response["runId"], wait=True)

    return workspace


def get_workspace(
    name_or_id: str,
    cluster_name_or_id: Optional[str] = None,
    non_interactive: bool = True,
    client: Optional[ServiceFoundryServiceClient] = None,
) -> Workspace:
    client = client or ServiceFoundryServiceClient.get_client()
    workspace, _ = resolve_workspace_or_error(
        name_or_id=name_or_id,
        cluster_name_or_id=cluster_name_or_id,
        non_interactive=non_interactive,
        client=client,
    )
    return workspace


def list_workspaces(
    cluster_name_or_id: Optional[str] = None,
    all_: bool = False,
    non_interactive: bool = True,
    client: Optional[ServiceFoundryServiceClient] = None,
):
    client = client or ServiceFoundryServiceClient.get_client()
    if all_:
        workspaces = all_workspaces(client=client)
    else:
        cluster = resolve_cluster_or_error(
            name_or_id=cluster_name_or_id,
            non_interactive=non_interactive,
            client=client,
        )
        console.print(PROMPT_USING_CLUSTER_CONTEXT.format(cluster.name))
        workspaces = resolve_workspaces(
            name_or_id=None,
            cluster_name_or_id=cluster,
            ignore_context=True,
            client=client,
        )
    return workspaces


def delete_workspace(
    name_or_id: str,
    cluster_name_or_id: Optional[str] = None,
    tail_logs: bool = True,
    non_interactive: bool = True,
    client: Optional[ServiceFoundryServiceClient] = None,
) -> Dict[str, Any]:
    client = client or ServiceFoundryServiceClient.get_client()
    workspace = get_workspace(
        name_or_id=name_or_id,
        cluster_name_or_id=cluster_name_or_id,
        non_interactive=non_interactive,
        client=client,
    )
    with console.status(
        PROMPT_REMOVING_WORKSPACE.format(workspace.name), spinner="dots"
    ):
        response = client.remove_workspace(workspace.id)
        if tail_logs:
            client.tail_logs(response["pipelinerun"]["name"], wait=True)
        ctx_workspace = client.session.get_workspace()
        if ctx_workspace:
            ctx_workspace = Workspace.from_dict(ctx_workspace)
            if ctx_workspace.id == workspace.id:
                client.session.set_workspace(None)
                console.print(
                    PROMPT_UNSETTING_WORKSPACE_CONTEXT.format(ctx_workspace.name)
                )
                client.session.save_session()
    return response
