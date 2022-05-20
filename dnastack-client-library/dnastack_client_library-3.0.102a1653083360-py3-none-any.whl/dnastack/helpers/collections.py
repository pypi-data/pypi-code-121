from imagination import container
from typing import TypeVar, Type, Optional

from dnastack.client.collections.client import CollectionServiceClient
from dnastack.client.data_connect import DataConnectClient
from dnastack.client.drs import DrsClient
from dnastack.configuration.models import ServiceEndpoint
from dnastack.helpers.client_factory import ConfigurationBasedClientFactory, ServiceEndpointNotFound

T = TypeVar('T', DataConnectClient, DrsClient)


def switch_to(endpoint: ServiceEndpoint, sub_client_class: Type[T]) -> T:
    """ Switch from a collection endpoint to a requested service client """
    factory: ConfigurationBasedClientFactory = container.get(ConfigurationBasedClientFactory)

    try:
        # Attempt to instantiate with the corresponding service information
        # from either a configuration or registered service registries.
        return factory.get(sub_client_class, endpoint_url=endpoint.url)
    except ServiceEndpointNotFound:
        # When all else fail, instantiate with the given endpoint.
        return sub_client_class.make(endpoint)


def switch_to_data_connect(client: CollectionServiceClient, id_or_slug_name: Optional[str] = None) -> DataConnectClient:
    """
    Switch from a Collection Service client to a Data-Connect client

    The argument "id_or_slug_name" is optional and some types of collection services ignore this argument.
    """
    return switch_to(client.data_connect_endpoint(id_or_slug_name), DataConnectClient)
