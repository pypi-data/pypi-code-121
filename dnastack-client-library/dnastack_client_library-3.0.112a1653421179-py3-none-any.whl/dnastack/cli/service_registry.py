from dataclasses import dataclass

from typing import Iterator, Optional, Dict

import click
from imagination import container

from dnastack.cli.exporter import to_json
from dnastack.cli.utils import command
from dnastack.client.service_registry.client import ServiceRegistry, STANDARD_SERVICE_REGISTRY_TYPE_V1_0
from dnastack.client.service_registry.helper import parse_ga4gh_service_info
from dnastack.common.logger import get_logger
from dnastack.configuration.manager import ConfigurationManager
from dnastack.configuration.models import ServiceEndpoint, EndpointSource


@click.group('registries')
def registry_command_group():
    """ Manage service registries """
    # The design of the command structure is inspired by "git remote"


@command(registry_command_group, 'list')
def list_registries():
    """ List registered service registries """
    click.echo(to_json([
        endpoint.dict(exclude_none=True)
        for endpoint in ServiceRegistryCommandHandler().get_registry_endpoint_iterator()
    ]))


@command(registry_command_group)
def add(registry_endpoint_id: str, registry_url: str):
    """
    Add a new service registry to the configuration and import all endpoints registered with it.

    The local ID of each imported endpoint will be "<registry_endpoint_id>:<external_id>".

    If there exists at least ONE service endpoints from the given registry then, throw an error.

    If the registry URL is already registered, then throw an error.
    """
    ServiceRegistryCommandHandler().add_registry_and_import_endpoints(registry_endpoint_id, registry_url)
    click.secho('Import completed', fg='green')


@command(registry_command_group)
def remove(registry_endpoint_id: str):
    """
    Remove the entry of the service registry from the configuration and remove all endpoints registered with it.
    """
    ServiceRegistryCommandHandler().remove_endpoints_associated_to(registry_endpoint_id)
    click.secho('Removal completed', fg='green')


@command(registry_command_group)
def sync(registry_endpoint_id: str):
    """
    Synchronize the service endpoints associated to the given service registry.

    This command will add new endpoints, update existing ones, and/or remove endpoints that are no longer registered
    with the given service registry.
    """
    ServiceRegistryCommandHandler().synchronize_endpoints(registry_endpoint_id)
    click.secho('Synchronization completed', fg='green')


@command(registry_command_group)
def list_endpoints(registry_endpoint_id: str):
    """ List all service endpoints imported from given registry """
    click.echo(to_json([
        endpoint.dict(exclude_none=True)
        for endpoint in ServiceRegistryCommandHandler().list_endpoints_associated_to(registry_endpoint_id)
    ]))


class ServiceRegistryCommandHandler:
    __output_color_map = {
        'add': 'green',
        'update': 'magenta',
        'keep': 'yellow',
        'remove': 'red',
    }

    def __init__(self):
        self.__logger = get_logger(type(self).__name__)
        self.__config_manager: ConfigurationManager = container.get(ConfigurationManager)

    def get_endpoint_iterator(self) -> Iterator[ServiceEndpoint]:
        for endpoint in self.__config_manager.load().endpoints:
            yield endpoint

    def get_registry_endpoint_iterator(self) -> Iterator[ServiceEndpoint]:
        for endpoint in self.get_endpoint_iterator():
            if endpoint.type not in ServiceRegistry.get_supported_service_types():
                continue
            yield endpoint

    def add_registry_and_import_endpoints(self, registry_endpoint_id: str, registry_url: str):
        config = self.__config_manager.load()
        all_endpoint_list = config.endpoints

        # When the endpoint ID already exists, throw an error.
        if [endpoint for endpoint in all_endpoint_list if endpoint.id == registry_endpoint_id]:
            raise EndpointAlreadyExisted(f'id = {registry_endpoint_id}')

        # When the registry URL is registered, throw an error.
        identical_registry_endpoint_ids = [
            endpoint.id
            for endpoint in all_endpoint_list
            if (endpoint.url == registry_url
                and endpoint.type == STANDARD_SERVICE_REGISTRY_TYPE_V1_0)
        ]
        if identical_registry_endpoint_ids:
            raise EndpointAlreadyExisted(f'This URL ({registry_url}) has already been registered locally with the '
                                         f'following ID(s): {", ".join(identical_registry_endpoint_ids)}')

        registry_endpoint = ServiceEndpoint(id=registry_endpoint_id,
                                            url=registry_url,
                                            type=STANDARD_SERVICE_REGISTRY_TYPE_V1_0)

        with self.__config_manager.load_then_save() as config:
            config.endpoints.append(registry_endpoint)
            self.__print_sync_operation('Registry', 'add', registry_endpoint)

        self.__synchronize_endpoints_with(ServiceRegistry.make(registry_endpoint))

    def synchronize_endpoints(self, registry_endpoint_id: str):
        config = self.__config_manager.load()

        filtered_endpoints = [
            endpoint
            for endpoint in config.endpoints
            if (endpoint.id == registry_endpoint_id
                and endpoint.type == STANDARD_SERVICE_REGISTRY_TYPE_V1_0)
        ]

        if not filtered_endpoints:
            raise RegistryNotFound(registry_endpoint_id)

        self.__synchronize_endpoints_with(ServiceRegistry.make(filtered_endpoints[0]))

    def __synchronize_endpoints_with(self, registry: ServiceRegistry):
        config = self.__config_manager.load()

        sync_operations: Dict[str, _SyncOperation] = {
            endpoint.id: _SyncOperation(action='keep', endpoint=endpoint)
            for endpoint in config.endpoints
        }

        # Mark all advertised endpoints as new or updated endpoints.
        for service_info in registry.list_services():
            endpoint = parse_ga4gh_service_info(service_info, f'{registry.endpoint.id}:{service_info.id}')
            endpoint.source = EndpointSource(source_id=registry.endpoint.id,
                                             external_id=service_info.id)
            sync_operations[endpoint.id] = _SyncOperation(action='update' if endpoint.id in sync_operations else 'add',
                                                          endpoint=endpoint)

        # Mark the existing associated endpoints for removal.
        for sync_operation in sync_operations.values():
            if not sync_operation.endpoint.source:
                continue

            if sync_operation.endpoint.source.source_id != registry.endpoint.id:
                continue

            if sync_operation.action != 'keep':
                continue

            sync_operation.action = 'remove'

        # Reconstruct the endpoint list.
        new_endpoint_list = []
        for sync_operation in sync_operations.values():
            if sync_operation.action in ('add', 'update', 'keep'):
                new_endpoint_list.append(sync_operation.endpoint)
            self.__print_sync_operation('Endpoint', sync_operation.action, sync_operation.endpoint)

        config.endpoints = sorted([sync_operation.endpoint for sync_operation in sync_operations.values()], key=lambda e: e.id)

        self.__config_manager.save(config)

    def remove_endpoints_associated_to(self, registry_endpoint_id: str):
        config = self.__config_manager.load()

        new_endpoint_list = []

        for endpoint in config.endpoints:
            if (
                    endpoint.id == registry_endpoint_id
                    or (endpoint.source and endpoint.source.source_id == registry_endpoint_id)
            ):
                self.__print_sync_operation('Registered Endpoint', 'remove', endpoint)
                continue
            else:
                new_endpoint_list.append(endpoint)
                self.__print_sync_operation('Registered Endpoint', 'keep', endpoint)

        config.endpoints = new_endpoint_list

        self.__config_manager.save(config)

    def list_endpoints_associated_to(self, registry_endpoint_id: str) -> Iterator[ServiceEndpoint]:
        config = self.__config_manager.load()

        for endpoint in config.endpoints:
            if endpoint.source is not None and endpoint.source.source_id == registry_endpoint_id:
                yield endpoint

    def __print_sync_operation(self, prefix: Optional[str], action: str, endpoint: ServiceEndpoint):
        if prefix:
            click.secho(f'{prefix}: ', dim=True, nl=False, err=True)

        action_color = self.__output_color_map[action]

        click.secho(f'{action.upper()} ', fg=action_color, nl=False, err=True)
        click.secho(
            f'{endpoint.id} ({endpoint.type.group}:{endpoint.type.artifact}:{endpoint.type.version}) at {endpoint.url}',
            err=True)


class RegistryNotFound(RuntimeError):
    def __init__(self, msg: str):
        super().__init__(msg)


class EndpointAlreadyExisted(RuntimeError):
    def __init__(self, msg: str):
        super().__init__(msg)


@dataclass
class _SyncOperation:
    action: str
    endpoint: ServiceEndpoint
