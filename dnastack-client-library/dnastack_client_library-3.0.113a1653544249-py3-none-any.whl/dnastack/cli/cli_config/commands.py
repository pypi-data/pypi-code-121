import click
import json
from click import BadParameter, Abort
from imagination import container
from pydantic import BaseModel
from typing import Dict, List, Optional, Any

from dnastack.helpers.client_factory import ConfigurationBasedClientFactory
from dnastack.cli.utils import handle_error_gracefully, show_alternative_for_deprecated_command
from dnastack.client.collections.client import CollectionServiceClient
from dnastack.client.data_connect import DataConnectClient
from dnastack.client.drs import DrsClient
from dnastack.client.service_registry.client import ServiceRegistry
from dnastack.configuration.exceptions import MissingEndpointError
from dnastack.configuration.manager import ConfigurationManager
from dnastack.configuration.models import Configuration, OAuth2Authentication, ServiceEndpoint
from dnastack.configuration.wrapper import ConfigurationWrapper
from dnastack.feature_flags import in_global_debug_mode
from dnastack.common.logger import get_logger
from dnastack.json_path import JsonPath, BrokenPropertyPathError

_full_schema = Configuration.schema()
_adapter_to_property_paths: Dict[str, List[str]] = dict()
_logger = get_logger('config')

service_adapter_types = [
    CollectionServiceClient.get_adapter_type(),
    DataConnectClient.get_adapter_type(),
    DrsClient.get_adapter_type(),
    ServiceRegistry.get_adapter_type(),
]


@click.group("config")
def config_command_group():
    """ Manage global configuration """


@config_command_group.command("schema", help="Show the schema of the configuration file")
@handle_error_gracefully
def config_schema():
    click.echo(json.dumps(_full_schema, indent=2, sort_keys=True))


@config_command_group.command("available-properties",
                              help="List all available configuration properties",
                              deprecated=True,
                              hidden=True)
@click.option("--type", "-t", required=False, default=None)
@handle_error_gracefully
def config_list_available_properties(type: Optional[str] = None):
    show_alternative_for_deprecated_command('dnastack endpoints available-properties')
    __show_available_properties(type)


def __show_available_properties(adapter_type: Optional[str] = None):
    print()

    click.secho('                                          ', bold=True, bg='blue')
    click.secho('  All available configuration properties  ', bold=True, bg='blue')
    click.secho('                                          ', bold=True, bg='blue')

    click.echo('\nPlease check out https://docs.viral.ai/analytics for more information.')

    adapter_to_property_paths = __get_known_adapter_to_property_paths()

    for service_adapter_name, service_property_paths in adapter_to_property_paths.items():
        if adapter_type and adapter_type != service_adapter_name:
            continue
        click.secho(f'\n{service_adapter_name}\n', bold=True)
        for service_property_path in service_property_paths:
            if service_property_path == 'adapter_type':
                continue  # This is an internal property. Permanently skip.
            if service_property_path == 'default':
                continue  # This is temporarily skipped until the CLI support multiple endpoint.
            click.secho(f'  · {service_adapter_name}.{service_property_path}')

    print()


def __get_known_adapter_to_property_paths() -> Dict[str, List[str]]:
    if not _adapter_to_property_paths:
        __resolve_reference(_full_schema)
        service_property_paths = __list_all_json_path(_full_schema['properties']['endpoints']['items'])

        for service_adapter_name in service_adapter_types:
            _adapter_to_property_paths[service_adapter_name] = list()
            for service_property_path in service_property_paths:
                if service_property_path in ['id', 'adapter_type']:
                    continue  # This is an internal property. Permanently skip.
                _adapter_to_property_paths[service_adapter_name].append(service_property_path)

    return _adapter_to_property_paths


def __list_all_json_path(obj: Dict[str, Any], prefix_path: List[str] = None) -> List[str]:
    properties = obj.get('properties') or dict()
    paths = []

    prefix_path = prefix_path or list()

    if len(prefix_path) == 1 and prefix_path[0] == 'authentication':
        return [
            f'{prefix_path[0]}.{oauth2_path}'
            for oauth2_path in __list_all_json_path(OAuth2Authentication.schema())
        ]
    else:
        if obj['type'] == 'object':
            for property_name, obj_property in properties.items():
                if 'anyOf' in obj_property:
                    for property_to_resolve in obj_property['anyOf']:
                        paths.extend(__list_all_json_path(__fetch_reference(property_to_resolve['$ref'], _full_schema),
                                                          prefix_path + [property_name]))
                elif obj_property['type'] == 'object':
                    paths.extend(__list_all_json_path(obj_property, prefix_path + [property_name]))
                elif obj_property['type'] == 'array':
                    paths.extend(__list_all_json_path(obj_property['items'], prefix_path + [property_name]))
                    paths.extend(__list_all_json_path(obj_property['items'], prefix_path + [property_name + '[i]']))
                else:
                    prefix_path_string = '.'.join(prefix_path)
                    paths.append(f'{prefix_path_string}{"." if prefix_path_string else ""}{property_name}')

    return sorted(paths)


def __fetch_reference(reference_url: str, root: Dict[str, Any]):
    if reference_url.startswith('#/'):
        ref_path = reference_url[2:].split(r'/')
        local_reference = root
        try:
            while ref_path:
                property_name = ref_path.pop(0)
                local_reference = local_reference[property_name]
        except KeyError as e:
            raise RuntimeError(f'The reference {reference_url} for the configuration is undefined.')
        return __resolve_reference(local_reference, root)
    raise NotImplementedError('Resolving an external reference is not supported.')


def __resolve_reference(obj: Dict[str, Any], root: Optional[Dict[str, Any]] = None):
    root = root or obj
    properties = obj.get('properties') or dict()
    for property_name, obj_property in properties.items():
        if obj_property.get('$ref'):
            properties[property_name] = __fetch_reference(obj_property.get('$ref'), root)
        # Deal with array
        if obj_property.get('items') and obj_property.get('items').get('$ref'):
            obj_property['items'] = __fetch_reference(obj_property.get('items').get('$ref'), root)

    return obj


@config_command_group.command("set-default", deprecated=True, hidden=True)
@click.argument("adapter_type", required=True)
@click.argument("endpoint_id", required=False, default=None)
@handle_error_gracefully
def set_default(adapter_type: str, endpoint_id: Optional[str] = None):
    service_types = ConfigurationBasedClientFactory.convert_from_short_type_to_full_types(adapter_type)

    config_manager: ConfigurationManager = container.get(ConfigurationManager)
    with config_manager.load_then_save() as config:
        config.set_default(adapter_type=adapter_type,
                           endpoint_id=endpoint_id,
                           service_types=service_types)


@config_command_group.command("remove-endpoint", deprecated=True, hidden=True)
@click.argument("adapter_type", required=True)
@click.argument("endpoint_id", required=True)
@handle_error_gracefully
def remove_endpoint(adapter_type: str, endpoint_id: str):
    config_manager: ConfigurationManager = container.get(ConfigurationManager)
    with config_manager.load_then_save() as config:
        config.remove_endpoint(adapter_type=adapter_type,
                               endpoint_id=endpoint_id)


@config_command_group.command("add-endpoint", deprecated=True, hidden=True)
@click.argument("adapter_type", required=True)
@click.argument("endpoint_id", required=True)
@click.argument("url", required=False, default=None)
@handle_error_gracefully
def add_endpoint(adapter_type: str, endpoint_id: str, url: str):
    service_types = ConfigurationBasedClientFactory.convert_from_short_type_to_full_types(adapter_type)

    config_manager: ConfigurationManager = container.get(ConfigurationManager)
    with config_manager.load_then_save() as config:
        __fix_endpoint_after_setting(endpoint=config.add_endpoint(adapter_type=adapter_type,
                                                                  endpoint_id=endpoint_id,
                                                                  url=url,
                                                                  service_types=service_types),
                                     path_defaults=dict(type=service_types[0]))


@config_command_group.command("list", deprecated=True, hidden=True)
def config_list():
    config_manager: ConfigurationManager = container.get(ConfigurationManager)
    click.secho(config_manager.load_raw() or '{}', dim=True)


@config_command_group.command("get", deprecated=True, hidden=True)
@click.argument("key")
@click.option("--endpoint-id", "-i", required=False, type=str, default=None)
@handle_error_gracefully
def config_get(key: str, endpoint_id: str):
    _logger.debug(f'GET {key}')

    adapter_type, path = __parse_configuration_key(key)
    service_types = ConfigurationBasedClientFactory.convert_from_short_type_to_full_types(adapter_type)
    config_manager: ConfigurationManager = container.get(ConfigurationManager)
    configuration: ConfigurationWrapper = config_manager.load_wrapper()

    try:
        endpoint = (
            configuration.get_endpoint(adapter_type=adapter_type,
                                       service_types=service_types,
                                       endpoint_id=endpoint_id,
                                       create_if_missing=False)
            if endpoint_id
            else configuration.get_default_endpoint(adapter_type=adapter_type,
                                                    service_types=service_types)
        )

        try:
            result = JsonPath.get(endpoint, path)
        except BrokenPropertyPathError as broken_path_error:
            if in_global_debug_mode:
                raise broken_path_error
            else:
                raise Abort(f'The configuration {key} does not exist.')
    except MissingEndpointError:
        result = None

    if result is None:
        click.secho('null', dim=True)
    elif isinstance(result, bool):
        click.secho(str(result).lower(), dim=True)
    elif isinstance(result, BaseModel):
        click.secho(result.json(indent=2), dim=True)
    else:
        click.secho(result, dim=True)


@config_command_group.command("set", deprecated=True, hidden=True)
@click.argument("key")
@click.argument("value")
@click.option("--endpoint-id", "-i", required=False, type=str, default=None)
@handle_error_gracefully
def config_set(key: str, value: str, endpoint_id: str):
    _logger.debug(f'SET {key} {value} (endpoint_id = {endpoint_id})')

    adapter_type, path = __parse_configuration_key(key)
    service_types = ConfigurationBasedClientFactory.convert_from_short_type_to_full_types(adapter_type)
    config_manager: ConfigurationManager = container.get(ConfigurationManager)

    with config_manager.load_then_save() as configuration:
        endpoint = (
            configuration.get_endpoint(adapter_type=adapter_type,
                                       service_types=service_types,
                                       endpoint_id=endpoint_id,
                                       create_if_missing=True)
            if endpoint_id
            else configuration.get_default_endpoint(adapter_type=adapter_type,
                                                    service_types=service_types,
                                                    create_if_missing=True)
        )

        try:
            JsonPath.set(endpoint, path, value)
        except BrokenPropertyPathError as __:
            _logger.debug(f'config_set: BROKEN SETTER: endpoint => {endpoint}')
            _logger.debug(f'config_set: BROKEN SETTER: path => {path}')
            # Attempt to repair the broken path.
            parent_path = '.'.join(path.split('.')[:-1])
            __repair_path(endpoint, parent_path)

            # Then, try again.
            try:
                JsonPath.set(endpoint, path, value)
            except BrokenPropertyPathError as e:
                if in_global_debug_mode:
                    raise e
                else:
                    raise Abort(f'The configuration {key} does not exist.')

        __fix_endpoint_after_setting(endpoint, dict(type=service_types[0]))


@config_command_group.command("unset", deprecated=True, hidden=True)
@click.argument("key")
@click.option("--endpoint-id", "-i", required=False, type=str, default=None)
def config_unset(key: str, endpoint_id: str):
    _logger.debug(f'UNSET {key}')

    adapter_type, path = __parse_configuration_key(key)
    service_types = ConfigurationBasedClientFactory.convert_from_short_type_to_full_types(adapter_type)
    config_manager: ConfigurationManager = container.get(ConfigurationManager)
    with config_manager.load_then_save() as configuration:
        endpoint = (
            configuration.get_endpoint(adapter_type=adapter_type,
                                       service_types=service_types,
                                       endpoint_id=endpoint_id,
                                       create_if_missing=False)
            if endpoint_id
            else configuration.get_default_endpoint(adapter_type=adapter_type,
                                                    service_types=service_types)
        )

        try:
            JsonPath.set(endpoint, path, None)
            # This is to ensure that the required properties are set to the default value.
            __repair_path(endpoint, path)
        except BrokenPropertyPathError as __:
            # The path does not exist. Nothing to unset.
            return

        __fix_endpoint_after_setting(endpoint, dict(type=service_types[0]))


def __fix_endpoint_after_setting(endpoint: ServiceEndpoint, path_defaults: Dict[str, Any]):
    """ Fix the endpoint configuration where the default value of the property can be dynamic """
    for path, default_value in path_defaults.items():
        current_value = JsonPath.get(endpoint, path)
        if current_value is None:
            JsonPath.set(endpoint, path, default_value)

    if endpoint.model_version == 1.0:
        endpoint.model_version = 2.0

    if endpoint.model_version <= 2.0:
        endpoint.adapter_type = None
        endpoint.mode = None


def __repair_path(obj, path: str, overridden_path_defaults: Dict[str, Any] = None):
    overridden_path_defaults = overridden_path_defaults or dict()

    selectors = path.split(r'.')
    visited = []

    _logger.debug(f'__repair_path: ENTER: type(obj) => {type(obj).__name__}')
    _logger.debug(f'__repair_path: ENTER: obj => {obj}')
    _logger.debug(f'__repair_path: ENTER: path => {path}')

    for selector in selectors:
        visited.append(selector)
        route = '.'.join(visited)

        _logger.debug(f'__repair_path: LOOP: route = {route}')

        try:
            JsonPath.get(obj, route, raise_error_on_null=True)
            break
        except BrokenPropertyPathError as e:
            visited_nodes = e.visited_path.split(r'.')
            last_visited_node = visited_nodes[-1]

            node = e.parent or obj

            _logger.debug(f'__repair_path: LOOP: ***** Broken Path Detected *****')
            _logger.debug(f'__repair_path: LOOP: type(e.parent) => {type(e.parent).__name__}')
            _logger.debug(f'__repair_path: LOOP: e.parent => {e.parent}')
            _logger.debug(f'__repair_path: LOOP: last_visited_node => {last_visited_node}')

            annotation = node.__annotations__[last_visited_node]

            if hasattr(node, last_visited_node) and getattr(node, last_visited_node):
                _logger.debug(f'__repair_path: LOOP: No repair')
            elif str(annotation).startswith('typing.Union[') or str(annotation).startswith("typing.Optional["):
                # Dealing with Union/Optional
                _logger.debug(f'__repair_path: LOOP: Handling union and optional')
                _logger.debug(f'__repair_path: LOOP: annotation.__args__ => {annotation.__args__}')
                __initialize_default_value(node, last_visited_node, annotation.__args__[0])
            else:
                __initialize_default_value(node, last_visited_node, annotation)

            _logger.debug(f'__repair_path: LOOP: node = {getattr(node, last_visited_node)}')

    if path in overridden_path_defaults:
        JsonPath.set(obj, path, overridden_path_defaults.get(path))

    _logger.debug(f'__repair_path: EXIT: obj => {obj}')


def __initialize_default_value(node, property_name: str, annotation):
    if hasattr(node, property_name) and getattr(node, property_name) is not None:
        return
    elif str(annotation).startswith('typing.Dict['):
        setattr(node, property_name, dict())
    elif str(annotation).startswith('typing.List['):
        setattr(node, property_name, list())
    elif issubclass(annotation, BaseModel):
        required_properties = annotation.schema().get('required') or []
        placeholders = {
            p: __get_place_holder(annotation.__annotations__[p])
            for p in required_properties
        }
        setattr(node, property_name, annotation(**placeholders))
    else:
        setattr(node, property_name, annotation())


def __get_place_holder(cls):
    if cls == str:
        return ''
    elif cls == int or cls == float:
        return 0
    elif cls == bool:
        return False
    else:
        raise NotImplementedError(cls)


def __parse_configuration_key(key: str):
    nodes = key.split(r'.')

    adapter_type = nodes[0]
    path = '.'.join(nodes[1:])

    adapter_to_property_paths = __get_known_adapter_to_property_paths()

    if adapter_type not in adapter_to_property_paths:
        __show_available_properties()
        _logger.debug(f'Unknown adapter type: {adapter_type}')
        raise BadParameter(f'Unknown configuration key: {key}')

    if path and path not in adapter_to_property_paths[adapter_type]:
        __show_available_properties(adapter_type)
        _logger.debug(f'A/{adapter_type}: Unknown Path: {path}')
        _logger.debug(f'A/{adapter_type}: Available Paths: {adapter_to_property_paths[adapter_type]}')
        raise BadParameter(f'Unknown configuration key: {key}')

    return adapter_type, path
