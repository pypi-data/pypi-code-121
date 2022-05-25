# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains helper methods for asset service REST APIs."""

from ._restclient._azure_machine_learning_workspaces import AzureMachineLearningWorkspaces as rest_client

from azureml._base_sdk_common.service_discovery import get_service_url
from azureml.core import Workspace


def _get_workspace_uri_path(subscription_id, resource_group, workspace_name):
    return ('/subscriptions/{}/resourceGroups/{}/providers'
            '/Microsoft.MachineLearningServices'
            '/workspaces/{}').format(subscription_id, resource_group, workspace_name)


def _get_rest_client(ws: Workspace):
    host = get_service_url(
        ws._auth,
        _get_workspace_uri_path(
            ws._subscription_id,
            ws._resource_group,
            ws._workspace_name),
        ws._workspace_id,
        ws.discovery_url)

    return rest_client(
        credential=ws._auth,
        subscription_id=ws.subscription_id,
        base_url=host)
