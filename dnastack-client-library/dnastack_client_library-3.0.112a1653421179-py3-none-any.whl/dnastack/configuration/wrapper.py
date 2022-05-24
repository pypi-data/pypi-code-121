import sys

from pprint import pformat

from typing import List, Optional
from uuid import uuid4

from dnastack.client.service_registry.models import ServiceType
from dnastack.configuration.exceptions import MissingEndpointError, ConfigurationError
from dnastack.configuration.models import Configuration, ServiceEndpoint
from dnastack.feature_flags import in_global_debug_mode
from dnastack.common.logger import get_logger


class UnsupportedModelVersionError(RuntimeError):
    pass


class ConfigurationWrapper:
    def __init__(self, configuration: Configuration):
        self.__logger = get_logger('Configuration')
        self.__config = configuration

    @property
    def original(self):
        return self.__config

    @property
    def endpoints(self):
        return self.__config.endpoints

    def set_default(self, adapter_type: str, endpoint_id: str, service_types: List[ServiceType]):
        self.__debug_message(f'adapter_type = {adapter_type}, endpoint_id = {id}')

        if not endpoint_id or endpoint_id.lower() in ('none', 'null'):
            # Remove the default endpoint of that client type
            del self.__config.defaults[adapter_type]
        else:
            try:
                endpoint = self.get_endpoint(adapter_type=adapter_type,
                                             endpoint_id=endpoint_id,
                                             service_types=service_types)
            except MissingEndpointError:
                raise ConfigurationError(f"Could not set default, not {adapter_type} adapter with id {endpoint_id}")

            self.__config.defaults[adapter_type] = endpoint.id

    def remove_endpoint(self,
                        adapter_type: str,
                        endpoint_id: str):
        self.__debug_message(f'endpoint_id = {endpoint_id}')

        # Replace the list.
        self.__config.endpoints = [
            endpoint
            for endpoint in self.__config.endpoints
            if endpoint.id != endpoint_id
        ]

        if adapter_type in self.__config.defaults and self.__config.defaults[adapter_type] == endpoint_id:
            del self.__config.defaults[adapter_type]

    def add_endpoint(self,
                     endpoint_id: str,
                     adapter_type: str,
                     service_types: List[ServiceType],
                     url: str = None) -> ServiceEndpoint:
        self.__debug_message(f'adapter_type = {adapter_type}, url = {url}')

        existed_endpoints = self._get_all_endpoints_by(adapter_type, service_types, endpoint_id)
        if existed_endpoints:
            self.__logger.warning(f'Detected:\n{pformat(existed_endpoints, indent=2)}:')
            raise ConfigurationError(f"Unable to add a new endpoint with ID {endpoint_id} as there exists an endpoint "
                                     f"with the same ID.")

        endpoint = ServiceEndpoint(id=endpoint_id, adapter_type=adapter_type, url=url or '')
        self.endpoints.append(endpoint)

        if adapter_type in self.__config.defaults and not self.__config.defaults[adapter_type]:
            self.__config.defaults[adapter_type] = endpoint_id

        return endpoint

    def _get_all_endpoints_by(self,
                              adapter_type: Optional[str] = None,
                              service_types: List[ServiceType] = None,
                              endpoint_id: Optional[str] = None) -> List[ServiceEndpoint]:
        endpoints = []

        for endpoint in self.endpoints:
            # If the ID is specified, the other conditions will be ignored.
            if endpoint_id:
                if endpoint.id == endpoint_id:
                    endpoints.append(endpoint)
                    self.__debug_message(f'_get_all_endpoints_by: E/{endpoint.id}: HIT (endpoint.id)')
                continue
            else:
                if endpoint.model_version == 2.0:
                    if service_types and endpoint.type not in service_types:
                        self.__debug_message(f'_get_all_endpoints_by: E/{endpoint.id}: MISSED: type is not matched')
                        continue
                elif endpoint.model_version == 1.0:
                    if adapter_type and endpoint.adapter_type != adapter_type:
                        self.__debug_message(f'_get_all_endpoints_by: E/{endpoint.id}: MISSED: adapter_type is not matched')
                        continue
                else:
                    raise UnsupportedModelVersionError(endpoint.model_version)

                self.__debug_message(f'_get_all_endpoints_by: E/{endpoint.id}: HIT')
                endpoints.append(endpoint)

        return endpoints

    def get_default_endpoint(self,
                             adapter_type: str,
                             service_types: List[ServiceType],
                             create_if_missing: bool = False) -> Optional[ServiceEndpoint]:
        if self._adapter_type_can_have_default_endpoint(adapter_type) and adapter_type in self.__config.defaults:
            try:
                return self.get_endpoint(adapter_type=adapter_type,
                                         service_types=service_types,
                                         endpoint_id=self.__config.defaults[adapter_type],
                                         create_if_missing=False)
            except MissingEndpointError:
                raise MissingEndpointError(f'No default endpoint for "{adapter_type}"')
        else:
            if create_if_missing:
                return self.get_endpoint(adapter_type=adapter_type,
                                         service_types=service_types,
                                         create_if_missing=create_if_missing)
            else:
                raise MissingEndpointError(f'No default endpoint for "{adapter_type}"')

    def get_endpoint(self,
                     adapter_type: str,
                     service_types: List[ServiceType],
                     endpoint_id: Optional[str] = None,
                     create_if_missing: bool = False) -> ServiceEndpoint:
        endpoints: List[ServiceEndpoint] = self._get_all_endpoints_by(adapter_type, service_types, endpoint_id)
        endpoint: Optional[ServiceEndpoint] = endpoints[0] if endpoints else None

        # When the endpoint is not available...
        if endpoint is None:
            if create_if_missing:
                endpoint = ServiceEndpoint(id=str(uuid4()),
                                           adapter_type=adapter_type,
                                           service_types=service_types,
                                           url='')  # Leave to an empty URL
                self.endpoints.append(endpoint)
                if self._adapter_type_can_have_default_endpoint(adapter_type):
                    self.__config.defaults[adapter_type] = endpoint.id
            else:
                raise MissingEndpointError(f'The "{adapter_type}" endpoint #{endpoint_id or "?"} is not defined.')

        return endpoint

    @staticmethod
    def _adapter_type_can_have_default_endpoint(adapter_type: str) -> bool:
        return adapter_type not in {'registry'}

    def __debug_message(self, msg: str):
        if in_global_debug_mode and 'unittest' in sys.modules:
            sys.stderr.write(msg + '\n')
            sys.stderr.flush()
        else:
            self.__logger.debug(msg)
