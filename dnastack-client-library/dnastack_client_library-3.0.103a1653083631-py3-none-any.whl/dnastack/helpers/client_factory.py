from imagination.decorator import service
from typing import Optional, Type, List

from dnastack.client.constants import SERVICE_CLIENT_CLASS, ALL_SERVICE_CLIENT_CLASSES
from dnastack.client.service_registry.client import ServiceRegistry
from dnastack.client.service_registry.factory import ClientFactory, UnregisteredServiceEndpointError
from dnastack.client.service_registry.models import ServiceType
from dnastack.common.logger import get_logger
from dnastack.configuration.exceptions import MissingEndpointError
from dnastack.configuration.manager import ConfigurationManager
from dnastack.configuration.models import ServiceEndpoint
from dnastack.configuration.wrapper import ConfigurationWrapper


class ServiceEndpointNotFound(RuntimeError):
    """ Raised when the requested service endpoint is not found """


class UnknownAdapterTypeError(RuntimeError):
    """ Raised when the given service adapter/short type is not registered or supported """


class NoServiceRegistryError(RuntimeError):
    """ Raised when there is no service registry to use """
    def __init__(self):
        super(NoServiceRegistryError, self).__init__('No service registry defined in the configuration')


class UnknownClientShortTypeError(RuntimeError):
    """ Raised when a given short service type is not recognized """


@service.registered()
class ConfigurationBasedClientFactory:
    """
    Configuration-based Client Factory

    This class will provide a service client based on the CLI configuration.
    """

    def __init__(self, config_manager: ConfigurationManager):
        self._config_manager = config_manager
        self._logger = get_logger(type(self).__name__)

    def get(self,
            cls: Type[SERVICE_CLIENT_CLASS],
            endpoint_id: Optional[str] = None,
            endpoint_url: Optional[str] = None) -> SERVICE_CLIENT_CLASS:
        return cls.make(
            self.get_endpoint(
                self._config_manager.load_wrapper(),
                cls,
                endpoint_id,
                endpoint_url,
            )
        )

    def get_service_registry_client_factory(self) -> ClientFactory:
        clients = [
            ServiceRegistry.make(endpoint)
            for endpoint in self._config_manager.load().endpoints
            if (
                    (endpoint.model_version == 1.0 and endpoint.adapter_type == ServiceRegistry.get_adapter_type())
                    or (
                            endpoint.model_version == 2.0 and endpoint.type in ServiceRegistry.get_supported_service_types())
            )
        ]

        if not clients:
            raise NoServiceRegistryError()

        return ClientFactory(clients)

    def get_endpoint(self,
                     configuration: ConfigurationWrapper,
                     cls: Type[SERVICE_CLIENT_CLASS],
                     endpoint_id: Optional[str] = None,
                     endpoint_url: Optional[str] = None,
                     create_default_if_missing: bool = False) -> ServiceEndpoint:
        adapter_type = cls.get_adapter_type()
        service_types = self.convert_from_short_type_to_full_types(adapter_type)

        # When the ID is given, this method will only return the endpoint by the ID.
        if endpoint_id:
            try:
                return configuration.get_endpoint(adapter_type=adapter_type,
                                                  service_types=service_types,
                                                  endpoint_id=endpoint_id,
                                                  create_if_missing=create_default_if_missing)
            except MissingEndpointError:
                raise ServiceEndpointNotFound(f'Requested ID = {endpoint_id}, Available IDs: {", ".join([e.id for e in configuration.endpoints])}')

        # When the URL is given, this method will get the endpoint by the URL from the configuration first. If there is
        # no service endpoint, then the method will attempt to get it from the registered service registries.
        if endpoint_url:
            filtered_endpoint_list = [
                endpoint
                for endpoint in configuration.endpoints
                if (
                        endpoint.url == endpoint_url
                        and endpoint.type in cls.get_supported_service_types()
                )
            ]

            if filtered_endpoint_list:
                return filtered_endpoint_list[0]
            else:
                raise ServiceEndpointNotFound(f'URL = {endpoint_url}')
                # try:
                #     return self.get_service_registry_client_factory().find_one_service_info(cls, endpoint_url)
                # except (NoServiceRegistryError, UnregisteredServiceEndpointError):
                #     raise ServiceEndpointNotFound(f'URL = {endpoint_url}')

        # If no filter is provided, use the default endpoint.
        try:
            return configuration.get_default_endpoint(
                adapter_type=adapter_type,
                service_types=self.convert_from_short_type_to_full_types(adapter_type)
            )
        except MissingEndpointError:
            raise ServiceEndpointNotFound(f'No default endpoint defined')

    @staticmethod
    def get_client_class(adapter_type: str) -> Type[SERVICE_CLIENT_CLASS]:
        for cls in ALL_SERVICE_CLIENT_CLASSES:
            if adapter_type == cls.get_adapter_type():
                return cls
        raise UnknownAdapterTypeError(adapter_type)

    @staticmethod
    def convert_from_short_type_to_full_types(short_type: str) -> List[ServiceType]:
        for client_class in ALL_SERVICE_CLIENT_CLASSES:
            if client_class.get_adapter_type() == short_type:
                return client_class.get_supported_service_types()
        raise UnknownClientShortTypeError(short_type)
