from typing import TypeVar

from dnastack.client.base_client import BaseServiceClient
from dnastack.client.collections.client import CollectionServiceClient
from dnastack.client.data_connect import DataConnectClient
from dnastack.client.drs import DrsClient
from dnastack.client.service_registry.client import ServiceRegistry

# All known client classes
ALL_SERVICE_CLIENT_CLASSES = (CollectionServiceClient, DataConnectClient, DrsClient, ServiceRegistry)

# All client classes for data access
DATA_SERVICE_CLIENT_CLASSES = (CollectionServiceClient, DataConnectClient, DrsClient)


SERVICE_CLIENT_CLASS = TypeVar('SERVICE_CLIENT_CLASS',
                               BaseServiceClient,
                               CollectionServiceClient,
                               DataConnectClient,
                               DrsClient,
                               ServiceRegistry)