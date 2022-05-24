# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains helper methods for asset service REST APIs."""

import os
from azureml.dataprep.api._loggerfactory import _LoggerFactory
from ._restclient._azure_machine_learning_workspaces import AzureMachineLearningWorkspaces as rest_client
from ._azureml_token_authentication import AzureMLTokenAuthentication

# ENV VARIABLE KEY FROM RUN CONTEXT
HISTORY_SERVICE_ENDPOINT_KEY = 'AZUREML_SERVICE_ENDPOINT'
AZUREML_ARM_SUBSCRIPTION_KEY = 'AZUREML_ARM_SUBSCRIPTION'
AZUREML_ARM_RESOURCEGROUP_KEY = 'AZUREML_ARM_RESOURCEGROUP'
AZUREML_ARM_WORKSPACE_NAME_KEY = 'AZUREML_ARM_WORKSPACE_NAME'

# SOTRAGE OPTIONS KEY
STORAGE_OPTION_KEY_AZUREML_SUBSCRIPTION = 'subscription'
STORAGE_OPTION_KEY_AZUREML_RESOURCEGROUP = 'resource_group'
STORAGE_OPTION_KEY_AZUREML_WORKSPACE = 'workspace'
STORAGE_OPTION_KEY_AZUREML_LOCATION = 'location'

_logger = None


def _get_logger():
    global _logger
    if _logger is None:
        _logger = _LoggerFactory.get_logger(__name__)
    return _logger


def _try_get_and_validate_workspace_info(storage_options=None):
    # try to get workspace information from environment variable for remote run
    try:
        subscription_id = os.environ.get(AZUREML_ARM_SUBSCRIPTION_KEY)
        resource_group = os.environ.get(AZUREML_ARM_RESOURCEGROUP_KEY)
        workspace_name = os.environ.get(AZUREML_ARM_WORKSPACE_NAME_KEY)

        if storage_options is None:
            storage_options = {}

        if subscription_id is not None:
            storage_options[STORAGE_OPTION_KEY_AZUREML_SUBSCRIPTION] = subscription_id

        if resource_group is not None:
            storage_options[STORAGE_OPTION_KEY_AZUREML_RESOURCEGROUP] = resource_group

        if workspace_name is not None:
            storage_options[STORAGE_OPTION_KEY_AZUREML_WORKSPACE] = workspace_name
    except:
        pass

    if storage_options is None \
            or storage_options.get(STORAGE_OPTION_KEY_AZUREML_SUBSCRIPTION, None) is None \
            or storage_options.get(STORAGE_OPTION_KEY_AZUREML_RESOURCEGROUP, None) is None \
            or storage_options.get(STORAGE_OPTION_KEY_AZUREML_WORKSPACE, None) is None:
        _LoggerFactory.trace(_logger, 'storage_options is missing for fetching data asset')
        raise ValueError(f'Missing required workspace information '
                         f'`{STORAGE_OPTION_KEY_AZUREML_SUBSCRIPTION}`, '
                         f'`{STORAGE_OPTION_KEY_AZUREML_RESOURCEGROUP}`, '
                         f'`{STORAGE_OPTION_KEY_AZUREML_WORKSPACE}`')

    return storage_options


def _get_aml_service_base_url(location=None):
    host_env = os.environ.get(HISTORY_SERVICE_ENDPOINT_KEY)

    # default to master
    if host_env is None:
        if location is None or location == 'centraluseuap':
            host_env = 'https://master.api.azureml-test.ms'
        else:
            host_env = F'https://{location}.api.azureml.ms'

    return host_env


def _get_rest_client(storage_options, auth):
    location = storage_options.get(STORAGE_OPTION_KEY_AZUREML_LOCATION, None)
    base_url = _get_aml_service_base_url(location)
    return rest_client(
        credential=auth,
        subscription_id=storage_options[STORAGE_OPTION_KEY_AZUREML_SUBSCRIPTION],
        base_url=base_url)


def _get_data_asset_by_id(asset_id, storage_options=None):
    auth = AzureMLTokenAuthentication._initialize_aml_token_auth()
    if auth is None:
        from azure.identity import AzureCliCredential
        auth = AzureCliCredential()

    storage_options = _try_get_and_validate_workspace_info(storage_options)
    client = _get_rest_client(storage_options, auth)
    asset = client.data_version.get_by_asset_id(
        storage_options[STORAGE_OPTION_KEY_AZUREML_SUBSCRIPTION],
        storage_options[STORAGE_OPTION_KEY_AZUREML_RESOURCEGROUP],
        storage_options[STORAGE_OPTION_KEY_AZUREML_WORKSPACE],
        {'value': asset_id},
    )
    return asset

