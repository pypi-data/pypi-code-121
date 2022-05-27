from urllib.parse import urlparse

import hashlib
from json import dumps

from pydantic import BaseModel
from traceback import format_exc
from typing import List, Any, Dict, Optional, Iterable, Type, TypeVar, Union, Iterator, Set

from dnastack.client.base_client import BaseServiceClient
from dnastack.client.constants import SERVICE_CLIENT_CLASS
from dnastack.client.service_registry.client import ServiceRegistry
from dnastack.client.service_registry.helper import parse_ga4gh_service_info
from dnastack.client.service_registry.models import ServiceType, Service
from dnastack.configuration.models import ServiceEndpoint
from dnastack.common.logger import get_logger

T = TypeVar('T')


class ServiceEndpointNotFound(RuntimeError):
    """ Raised when the requested service endpoint is not found """


class UnsupportedClientClassError(RuntimeError):
    """ Raised when the given client class is not supported """

    def __init__(self, cls: Type):
        super(UnsupportedClientClassError, self).__init__(f'{cls.__module__}.{cls.__name__} is not supported')


class UnregisteredServiceEndpointError(ServiceEndpointNotFound):
    """ Raised when the requested service endpoint is not registered """

    def __init__(self, services: Iterable[Service]):
        alternative_endpoint_urls = ', '.join(sorted([
            f'{service.url} ({service.type.group}:{service.type.artifact}:{service.version})'
            for service in services
        ]))
        super(UnregisteredServiceEndpointError, self).__init__(
            f'Try alternative(s): {alternative_endpoint_urls}'
            if alternative_endpoint_urls
            else 'No alternatives'
        )


class RegisteredServiceInfo(BaseModel):
    source_url: str
    info: Service


class RegisteredServiceEndpoint(BaseModel):
    source_url: str
    endpoint: ServiceEndpoint


class ClientFactory:
    """ Service Client Factory using Service Registries """

    def __init__(self, registries: List[ServiceRegistry]):
        self.__logger = get_logger(type(self).__name__)
        self.__registries = registries

    def all_service_infos(self) -> Iterator[RegisteredServiceInfo]:
        entries = []

        for registry in self.__registries:
            # noinspection PyBroadException
            try:
                for service in registry.list_services():
                    entries.append(RegisteredServiceInfo(source_url=registry.url,
                                                         info=service))
            except:
                self.__logger.warning(format_exc())
                self.__logger.warning(f'Unable to retrieve the list of services from {registry.url}')

        # TODO: Merging all authentication informations for different endpoints.
        #       Only need to merge "resource_url" and "scope"... everything else must be the same.
        self._merge_auth_info_list(entries)

        for entry in entries:
            yield entry

    def _merge_auth_info_list(self, entries: List[RegisteredServiceInfo]):
        auth_info_groups: Dict[str, List[Dict[str, Any]]] = dict()
        for entry in entries:
            for auth_info in (entry.info.authentication or []):
                if auth_info.get('type') is None or auth_info.get('type') == 'oauth2':
                    if 'resource' not in auth_info:
                        self.__logger.warning(f'R/{entry.source_url}: S/{entry.info.id}: Skipped from merging as The '
                                              f'resource URL is not specified.')
                        continue
                else:
                    self.__logger.warning(f'R/{entry.source_url}: S/{entry.info.id}: Skipped from merging as it is '
                                          f'not OAuth2.')
                    continue

                group_key = self._make_auth_info_group_key(auth_info)
                if group_key not in auth_info_groups:
                    auth_info_groups[group_key] = list()
                auth_info_groups[group_key].append(auth_info)

        for group_key, auth_info_list in auth_info_groups.items():
            self._merge_auth_info_per_group(auth_info_list)

    def _merge_auth_info_per_group(self, auth_info_list: List[Dict[str, Any]]):
        # This is a special keyword. When the original scope is empty or undefined, it is assumed that the client will
        # request for all scopes. This special keyword will reset the scope set so that the client will not specify
        # the scope during the authentication.
        ALL_SCOPES = '<all>'

        # The current implementation makes an optimistic assumption that when the client has authorization for
        # a resource at the root level, i.e., https://foo.io/, it will have access to all resources as long as
        # all necessary scopes are requested.
        # TODO Compute the map based on the minimum request path.
        url_to_scopes_map: Dict[str, Set[str]] = dict()

        # Separate scopes per domain
        for auth_info in auth_info_list:
            resource_url = auth_info['resource']
            parsed_url = urlparse(resource_url)

            url = f'{parsed_url.scheme}://{parsed_url.netloc}/'

            if url not in url_to_scopes_map:
                url_to_scopes_map[url] = set()

            url_to_scopes_map[url].update(
                auth_info['scope'].split(' ')
                if auth_info.get('scope')
                else [ALL_SCOPES]
            )

        # Simplify the scope set if it contains ALL_SCOPES.
        for scopes in url_to_scopes_map.values():
            if ALL_SCOPES in scopes:
                scopes.clear()

        # Modify the auth info.
        for auth_info in auth_info_list:
            resource_url: str = auth_info['resource']

            for url, scopes in url_to_scopes_map.items():
                if resource_url.startswith(url):
                    auth_info['resource'] = url
                    auth_info['scope'] = ' '.join(sorted(scopes)) or None
                    break
                else:
                    continue

    def _make_auth_info_group_key(self, auth_info: Dict[str, Any]) -> str:
        content = dumps(
            {
                k: v
                for k, v in auth_info.items()
                if k not in ['resource', 'scope']
            },
            sort_keys=True
        )
        h = hashlib.new('sha256')
        h.update(content.encode('utf-8'))
        return h.hexdigest()

    def find_services(self,
                      url: Optional[str] = None,
                      types: Optional[List[ServiceType]] = None,
                      exact_match: bool = True) -> Iterable[Service]:
        """ Find GA4GH services """
        assert url or types, 'Either url or types must be defined.'

        self.__logger.debug(f'find_services: [url: {url}] [types: {types}] [exact_match: {exact_match}]')

        for entry in self.all_service_infos():
            service = entry.info

            if url:
                if exact_match:
                    if service.url != url:
                        continue
                else:
                    if not service.url.startswith(url):
                        continue

            if types and not self._contain_type(service.type, types, exact_match):
                continue

            yield entry.info

    def find_one_service_info(self,
                              client_class: Type[SERVICE_CLIENT_CLASS],
                              service_endpoint_url: str) -> ServiceEndpoint:
        if issubclass(client_class, BaseServiceClient):
            types = client_class.get_supported_service_types()

            # Return the client of the first matched service endpoint.
            for service in self.find_services(service_endpoint_url, types):
                return parse_ga4gh_service_info(service)

            self.__logger.info(f'The service ({service_endpoint_url}) is not found in any known service registries.')
            self.__logger.debug(f'Failed to match types ({types})')

            # At this point, no service endpoints are exactly matched. Compile information for the error feedback.
            raise UnregisteredServiceEndpointError(self.find_services(service_endpoint_url, types, exact_match=False))
        else:
            raise UnsupportedClientClassError(client_class)

    def create(self, client_class: Type[T], service_endpoint_url: str) -> T:
        if issubclass(client_class, BaseServiceClient):
            return client_class.make(self.find_one_service_info(client_class, service_endpoint_url))
        else:
            raise UnsupportedClientClassError(client_class)

    @staticmethod
    def _contain_type(anchor: ServiceType, types: List[ServiceType], exact_match: bool) -> bool:
        if exact_match:
            return anchor in types
        else:
            for given_type in types:
                if anchor.group == given_type.group and anchor.artifact == given_type.artifact:
                    return True
            return False

    @classmethod
    def use(cls, *service_registry_endpoints: Union[str, ServiceEndpoint]):
        """
        .. note:: This only works with public registries.
        """
        return cls([
            ServiceRegistry(
                endpoint
                if isinstance(endpoint, ServiceEndpoint)
                else ServiceEndpoint(url=endpoint)
            )
            for endpoint in service_registry_endpoints
        ])
