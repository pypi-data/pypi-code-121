from typing import Any, Dict, List, Optional

from servicefoundry.internal.clients.service_foundry_client import (
    ServiceFoundryServiceClient,
)
from servicefoundry.internal.lib.messages import (
    PROMPT_REMOVING_SERVICE,
    PROMPT_USING_WORKSPACE_CONTEXT,
)
from servicefoundry.internal.lib.util import (
    all_services,
    resolve_service_or_error,
    resolve_services,
    resolve_workspace_or_error,
)
from servicefoundry.internal.model.entity import Service


def get_service(
    name_or_id: str,
    workspace_name_or_id: Optional[str] = None,
    cluster_name_or_id: Optional[str] = None,
    non_interactive: bool = True,
    client: Optional[ServiceFoundryServiceClient] = None,
) -> Service:
    client = client or ServiceFoundryServiceClient.get_client()
    service, _, _ = resolve_service_or_error(
        name_or_id=name_or_id,
        workspace_name_or_id=workspace_name_or_id,
        cluster_name_or_id=cluster_name_or_id,
        non_interactive=non_interactive,
        client=client,
    )
    return service


def list_services(
    workspace_name_or_id: Optional[str] = None,
    cluster_name_or_id: Optional[str] = None,
    all_: bool = False,
    non_interactive: bool = True,
    client: Optional[ServiceFoundryServiceClient] = None,
) -> List[Service]:
    client = client or ServiceFoundryServiceClient.get_client()
    if all_:
        services = all_services(client=client)
    else:
        workspace, cluster = resolve_workspace_or_error(
            name_or_id=workspace_name_or_id,
            cluster_name_or_id=cluster_name_or_id,
            non_interactive=non_interactive,
            client=client,
        )
        console.print(PROMPT_USING_WORKSPACE_CONTEXT.format(workspace.name))
        services = resolve_services(
            client=client,
            name_or_id=None,
            workspace_name_or_id=workspace,
            cluster_name_or_id=cluster,
            ignore_context=True,
        )
    return services


def delete_service(
    name_or_id: str,
    workspace_name_or_id: Optional[str] = None,
    cluster_name_or_id: Optional[str] = None,
    tail_logs: bool = True,
    non_interactive: bool = True,
    client: Optional[ServiceFoundryServiceClient] = None,
) -> Dict[str, Any]:
    client = client or ServiceFoundryServiceClient.get_client()
    service = get_service(
        name_or_id=name_or_id,
        workspace_name_or_id=workspace_name_or_id,
        cluster_name_or_id=cluster_name_or_id,
        non_interactive=non_interactive,
        client=client,
    )
    with console.status(PROMPT_REMOVING_SERVICE.format(service.name), spinner="dots"):
        response = client.remove_service(service.id)
        if tail_logs:
            client.tail_logs(response["runId"])
    return response
