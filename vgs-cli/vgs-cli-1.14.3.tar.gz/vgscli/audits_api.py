import logging

from copy import deepcopy
from simple_rest_client.api import API
from simple_rest_client.resource import Resource

from vgscli._version import __version__
from vgscli.errors import VaultNotFoundError
from typing import Dict

logger = logging.getLogger(__name__)

env_url = {
    'dev': 'https://audits.verygoodsecurity.io',
    'prod': 'https://audits.apps.verygood.systems',
}


class AccessLogsResource(Resource):
    actions = {
        'retrieve': {'method': 'GET', 'url': 'access-logs/{}'},
        'list': {'method': 'GET', 'url': 'access-logs'},
    }


class OperationsLogsResource(Resource):
    actions = {
        'list': {'method': 'GET', 'url': 'op-pipeline-logs'},
    }

class OperationLogsQueryConfig:

    TENANT_ID_KEY = 'filter[tenant_id]'
    TRACE_ID_KEY = 'filter[trace_id]'

    PAGE_SIZE_KEY = 'page[size]'

    def __init__(self, tenant_id: str, trace_id: str, page_size: int = 1000):
        self._configs: Dict[str, str] = {
            OperationLogsQueryConfig.TENANT_ID_KEY: tenant_id,
            OperationLogsQueryConfig.PAGE_SIZE_KEY: page_size,
            OperationLogsQueryConfig.TRACE_ID_KEY: trace_id
        }

    def to_query_params(self):
        return deepcopy({k: v for k, v in self._configs.items() if v is not None})

    @property
    def tenant_id(self):
        return self._configs.get(OperationLogsQueryConfig.TENANT_ID_KEY)

    @tenant_id.setter
    def tenant_id(self, value: str):
        self._configs[OperationLogsQueryConfig.TENANT_ID_KEY] = value

    @property
    def page_size(self):
        return self._configs.get(OperationLogsQueryConfig.PAGE_SIZE_KEY)

    @page_size.setter
    def page_size(self, value: str):
        self._configs[OperationLogsQueryConfig.PAGE_SIZE_KEY] = value

    @property
    def trace_id(self):
        return self._configs.get(OperationLogsQueryConfig.TRACE_ID_KEY)

    @page_size.setter
    def trace_id(self, value: str):
        self._configs[OperationLogsQueryConfig.TRACE_ID_KEY] = value


def create_api(ctx, vault_id, environment, token):
    api = API(
        api_root_url=env_url[environment],
        params={},  # default params
        headers={
            'VGS-Tenant': vault_id,
            'Content-Type': 'application/vnd.api+json',
            'Accept': 'application/vnd.api+json',
            'User-Agent': 'VGS CLI {}'.format(__version__),
            'Authorization': 'Bearer {}'.format(token)
        },  # default headers
        timeout=50,  # default timeout in seconds
        append_slash=False,  # append slash to final url
        json_encode_body=True,  # encode body as json
    )
    api.add_resource(resource_name='access_logs', resource_class=AccessLogsResource)
    api.add_resource(resource_name='operations_logs', resource_class=OperationsLogsResource)
    return api


def get_api_url(ctx, vault_id, api):
    response = api.accounts_api.get_vault_by_id(vault_id)
    try:
        return response.body['data'][0]['links']['vault_management_api']
    except (KeyError, IndexError):
        # if we weren't able to extract the vault_management_api it means that the provided vault_id doesn't exist
        raise VaultNotFoundError(vault_id, ctx)
