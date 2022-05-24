import click
from imagination import container
from pydantic import BaseModel
from typing import Dict, List, Any, Optional

from dnastack.cli.exporter import to_json
from dnastack.cli.utils import command, echo_header, ArgumentSpec
from dnastack.client.collections.client import \
    CollectionServiceClient, \
    STANDARD_COLLECTION_SERVICE_TYPE_V1_0, \
    EXPLORER_COLLECTION_SERVICE_TYPE_V1_0
from dnastack.client.constants import ALL_SERVICE_CLIENT_CLASSES, SERVICE_CLIENT_CLASS
from dnastack.client.data_connect import DataConnectClient, DATA_CONNECT_TYPE_V1_0
from dnastack.client.drs import DrsClient, DRS_TYPE_V1_1
from dnastack.common.logger import get_logger
from dnastack.common.simple_stream import SimpleStream
from dnastack.configuration.manager import ConfigurationManager
from dnastack.configuration.models import OAuth2Authentication, ServiceEndpoint
from dnastack.helpers.client_factory import ConfigurationBasedClientFactory
from dnastack.json_path import JsonPath, BrokenPropertyPathError


@click.group('endpoints')
def endpoint_command_group():
    """ Manage service endpoints """


@command(endpoint_command_group, 'available-properties')
def list_available_properties():
    """ List all available configuration property """
    config_properties = EndpointCommandHandler().list_available_properties()

    echo_header('General Configuration')

    SimpleStream(config_properties) \
        .filter(lambda p: not p.startswith('authentication.')) \
        .for_each(__show_config_property)

    echo_header('Authentication Configuration')

    # List the authentication info properties.
    # NOTE: While we still support the PAT flow, we are not advertising that method.
    SimpleStream(config_properties) \
        .filter(lambda p: p.startswith('authentication.')) \
        .filter(lambda p: not p.startswith('authentication.personal_access_')) \
        .for_each(__show_config_property)


def __show_config_property(config_property: str):
    click.secho('● ', dim=False, fg='blue', nl=False)
    click.secho(config_property)

    example_config_value = '...'
    if config_property.endswith('url') or config_property.endswith('endpoint'):
        example_config_value = 'https://...'
    if config_property.endswith('version'):
        example_config_value = '1.23.456'

    click.secho('  Examples:', dim=True, bold=True)
    click.secho(f'    ● dnastack endpoints get <ID> {config_property}', dim=True)
    click.secho(f'    ● dnastack endpoints set <ID> {config_property} "{example_config_value}"', dim=True)
    click.secho(f'    ● dnastack endpoints unset <ID> {config_property}', dim=True)
    print()


@command(endpoint_command_group, 'schema')
def show_schema():
    """
    Show the schema of the endpoint configuration

    This is mainly for development.
    """
    echo_header('Service Endpoint')
    click.echo(to_json(ServiceEndpoint.schema()))

    echo_header('OAuth2 Authentication Information')
    click.echo(to_json(OAuth2Authentication.schema()))


@command(endpoint_command_group, 'list')
def list_endpoints():
    """ List all registered service endpoint """
    click.echo(to_json([
        endpoint.dict(exclude_none=True)
        for endpoint in EndpointCommandHandler().list_endpoints()
    ]))


@command(endpoint_command_group,
         'add',
         specs=[
             ArgumentSpec(
                 name='short_type',
                 help='Client short type',
                 arg_names=['-t', '--type'],
                 as_option=True,
                 choices=[t.get_adapter_type() for t in ALL_SERVICE_CLIENT_CLASSES],
             ),
         ])
def add_endpoint(id: str, short_type: str):
    """ Add a new endpoint """
    EndpointCommandHandler().add_endpoint(id, short_type)


@command(endpoint_command_group, 'remove')
def remove_endpoint(id: str):
    """ Remove an endpoint """
    EndpointCommandHandler().remove_endpoint(id)


@command(endpoint_command_group, 'set')
def set_endpoint_property(id: str, config_property: str, config_value: str):
    """ Set the endpoint property """
    EndpointCommandHandler().set_endpoint_property(id, config_property, config_value)


@command(endpoint_command_group, 'unset')
def unset_endpoint_property(id: str, config_property: str):
    """ Unset the endpoint property """
    EndpointCommandHandler().set_endpoint_property(id, config_property, None)


@command(endpoint_command_group)
def get_defaults():
    """ Get the command-group-to-default-endpoint-id map """
    click.echo(to_json(EndpointCommandHandler().get_defaults()))


@command(endpoint_command_group)
def set_default(id: str):
    """ Set the given endpoint as the default for its type """
    EndpointCommandHandler().set_default(id)


@command(endpoint_command_group)
def unset_default(id: str):
    """ Unset the given endpoint as the default for its type """
    EndpointCommandHandler().unset_default(id)


class EndpointCommandHandler:
    def __init__(self):
        self.__logger = get_logger(type(self).__name__)
        self.__schema: Dict[str, Any] = self.__resolve_json_reference(ServiceEndpoint.schema())
        self.__config_manager: ConfigurationManager = container.get(ConfigurationManager)

    def get_defaults(self):
        return self.__config_manager.load().defaults

    def set_default(self, id: str):
        config = self.__config_manager.load()

        endpoint = SimpleStream(config.endpoints).filter(lambda e: e.id == id).find_first()
        if not endpoint:
            raise EndpointNotFound(id)

        config.defaults[self.__get_short_type(endpoint)] = id

        self.__config_manager.save(config)

    def unset_default(self, id: str):
        config = self.__config_manager.load()

        endpoint = SimpleStream(config.endpoints).filter(lambda e: e.id == id).find_first()
        if not endpoint:
            raise EndpointNotFound(id)

        del config.defaults[self.__get_short_type(endpoint)]

        self.__config_manager.save(config)

    def reset(self):
        configuration = self.__config_manager.load()
        configuration.defaults = dict()
        configuration.endpoints = list()
        self.__config_manager.save(configuration)

    def list_available_properties(self) -> List[str]:
        """ List all available configuration property """
        return SimpleStream(self.__list_all_json_path(self.__schema)) \
            .filter(lambda path: path not in ['id', 'adapter_type', 'mode', 'model_version']) \
            .to_list()

    def list_endpoints(self):
        """ List all registered service endpoint """
        return self.__config_manager.load().endpoints

    def add_endpoint(self, id: str, short_type: str):
        """ Add a new endpoint """
        full_types = ConfigurationBasedClientFactory.convert_from_short_type_to_full_types(short_type)

        config = self.__config_manager.load()

        first_existing_endpoint = SimpleStream(config.endpoints).filter(lambda e: e.id == id).find_first()
        if first_existing_endpoint:
            raise EndpointAlreadyExists(f'{id} ({first_existing_endpoint.type})')

        config.endpoints.append(ServiceEndpoint(id=id, type=full_types[0], url=''))

        if short_type not in config.defaults:
            config.defaults[short_type] = id

        self.__config_manager.save(config)

    def set_endpoint_property(self, id: str, config_property: str, config_value: Optional[str]):
        """ Set the endpoint property """
        config = self.__config_manager.load()
        endpoint = SimpleStream(config.endpoints).filter(lambda e: e.id == id).find_first()

        if endpoint is None:
            raise EndpointNotFound(id)

        if config_property not in self.list_available_properties():
            raise InvalidConfigurationProperty(config_property)

        try:
            JsonPath.set(endpoint, config_property, config_value)
        except BrokenPropertyPathError as __:
            self.__logger.debug(f'set_endpoint: BROKEN PATH: endpoint => {endpoint}')
            self.__logger.debug(f'set_endpoint: BROKEN PATH: config_property => {config_property}')
            # Attempt to repair the broken config_property.
            parent_path = '.'.join(config_property.split('.')[:-1])
            self.__repair_path(endpoint, parent_path)

            # Then, try again.
            JsonPath.set(endpoint, config_property, config_value)

        self.__fix_endpoint_after_setting(endpoint)
        self.__config_manager.save(config)

    def remove_endpoint(self, id: str):
        """ Remove an endpoint """
        config = self.__config_manager.load()

        # Recreate the list by excluding the one with the given ID.
        config.endpoints = SimpleStream(config.endpoints).filter(lambda e: e.id != id).to_list()

        # Remove the endpoint from the default endpoint map.
        for short_type in list(config.defaults.keys()):
            endpoint_id = config.defaults[short_type]
            if endpoint_id == id:
                del config.defaults[short_type]

        self.__config_manager.save(config)

    def __repair_path(self, obj, path: str, overridden_path_defaults: Dict[str, Any] = None):
        overridden_path_defaults = overridden_path_defaults or dict()

        selectors = path.split(r'.')
        visited = []

        self.__logger.debug(f'__repair_path: ENTER: type(obj) => {type(obj).__name__}')
        self.__logger.debug(f'__repair_path: ENTER: obj => {obj}')
        self.__logger.debug(f'__repair_path: ENTER: path => {path}')

        for selector in selectors:
            visited.append(selector)
            route = '.'.join(visited)

            self.__logger.debug(f'__repair_path: LOOP: route = {route}')

            try:
                JsonPath.get(obj, route, raise_error_on_null=True)
                break
            except BrokenPropertyPathError as e:
                visited_nodes = e.visited_path.split(r'.')
                last_visited_node = visited_nodes[-1]

                node = e.parent or obj

                self.__logger.debug(f'__repair_path: LOOP: ***** Broken Path Detected *****')
                self.__logger.debug(f'__repair_path: LOOP: type(e.parent) => {type(e.parent).__name__}')
                self.__logger.debug(f'__repair_path: LOOP: e.parent => {e.parent}')
                self.__logger.debug(f'__repair_path: LOOP: last_visited_node => {last_visited_node}')

                annotation = node.__annotations__[last_visited_node]

                if hasattr(node, last_visited_node) and getattr(node, last_visited_node):
                    self.__logger.debug(f'__repair_path: LOOP: No repair')
                elif str(annotation).startswith('typing.Union[') or str(annotation).startswith("typing.Optional["):
                    # Dealing with Union/Optional
                    self.__logger.debug(f'__repair_path: LOOP: Handling union and optional')
                    self.__logger.debug(f'__repair_path: LOOP: annotation.__args__ => {annotation.__args__}')
                    self.__initialize_default_value(node, last_visited_node, annotation.__args__[0])
                else:
                    self.__initialize_default_value(node, last_visited_node, annotation)

                self.__logger.debug(f'__repair_path: LOOP: node = {getattr(node, last_visited_node)}')

        if path in overridden_path_defaults:
            JsonPath.set(obj, path, overridden_path_defaults.get(path))

        self.__logger.debug(f'__repair_path: EXIT: obj => {obj}')

    def __initialize_default_value(self, node, property_name: str, annotation):
        if hasattr(node, property_name) and getattr(node, property_name) is not None:
            return
        elif str(annotation).startswith('typing.Dict['):
            setattr(node, property_name, dict())
        elif str(annotation).startswith('typing.List['):
            setattr(node, property_name, list())
        elif issubclass(annotation, BaseModel):
            required_properties = annotation.schema().get('required') or []
            placeholders = {
                p: self.__get_place_holder(annotation.__annotations__[p])
                for p in required_properties
            }
            setattr(node, property_name, annotation(**placeholders))
        else:
            setattr(node, property_name, annotation())

    def __get_place_holder(self, cls):
        if cls == str:
            return ''
        elif cls == int or cls == float:
            return 0
        elif cls == bool:
            return False
        else:
            raise NotImplementedError(cls)

    def __list_all_json_path(self, obj: Dict[str, Any], prefix_path: List[str] = None) -> List[str]:
        properties = obj.get('properties') or dict()
        paths = []

        prefix_path = prefix_path or list()

        if len(prefix_path) == 1 and prefix_path[0] == 'authentication':
            return [
                f'{prefix_path[0]}.{oauth2_path}'
                for oauth2_path in self.__list_all_json_path(OAuth2Authentication.schema())
            ]
        else:
            if obj['type'] == 'object':
                for property_name, obj_property in properties.items():
                    if 'anyOf' in obj_property:
                        for property_to_resolve in obj_property['anyOf']:
                            paths.extend(
                                self.__list_all_json_path(
                                    self.__fetch_json_reference(
                                        property_to_resolve['$ref'],
                                        self.__schema
                                    ),
                                    prefix_path + [property_name]
                                )
                            )
                    elif obj_property['type'] == 'object':
                        paths.extend(
                            self.__list_all_json_path(
                                obj_property,
                                prefix_path + [property_name]
                            )
                        )
                    elif obj_property['type'] == 'array':
                        paths.extend(
                            self.__list_all_json_path(
                                obj_property['items'],
                                prefix_path + [property_name]
                            )
                        )
                        paths.extend(
                            self.__list_all_json_path(
                                obj_property['items'],
                                prefix_path + [property_name + '[i]']
                            )
                        )
                    else:
                        prefix_path_string = '.'.join(prefix_path)
                        paths.append(f'{prefix_path_string}{"." if prefix_path_string else ""}{property_name}')

        return sorted(paths)

    def __resolve_json_reference(self, obj: Dict[str, Any], root: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        root = root or obj
        properties = obj.get('properties') or dict()
        for property_name, obj_property in properties.items():
            if obj_property.get('$ref'):
                properties[property_name] = self.__fetch_json_reference(obj_property.get('$ref'), root)
            # Deal with array
            if obj_property.get('items') and obj_property.get('items').get('$ref'):
                obj_property['items'] = self.__fetch_json_reference(obj_property.get('items').get('$ref'), root)

        return obj

    def __fetch_json_reference(self, reference_url: str, root: Dict[str, Any]):
        if reference_url.startswith('#/'):
            ref_path = reference_url[2:].split(r'/')
            local_reference = root
            try:
                while ref_path:
                    property_name = ref_path.pop(0)
                    local_reference = local_reference[property_name]
            except KeyError as e:
                raise RuntimeError(f'The reference {reference_url} for the configuration is undefined.')
            return self.__resolve_json_reference(local_reference, root)

        raise NotImplementedError('Resolving an external reference is not supported.')

    @staticmethod
    def __fix_endpoint_after_setting(endpoint: ServiceEndpoint):
        """
        Fix the endpoint configuration where the default value of the property can be dynamic

        This is designed for online migration for older endpoint configuration.
        """
        if endpoint.model_version is None or endpoint.model_version == 1.0:
            endpoint.model_version = 2.0

            if endpoint.adapter_type == CollectionServiceClient.get_adapter_type():
                endpoint.type = (
                    EXPLORER_COLLECTION_SERVICE_TYPE_V1_0
                    if endpoint.mode == 'explorer'
                    else STANDARD_COLLECTION_SERVICE_TYPE_V1_0
                )
            elif endpoint.adapter_type == DataConnectClient.get_adapter_type():
                endpoint.type = DATA_CONNECT_TYPE_V1_0
            elif endpoint.adapter_type == DrsClient.get_adapter_type():
                endpoint.type = DRS_TYPE_V1_1
            else:
                raise NotImplementedError(f'This type of endpoint ({endpoint.adapter_type}) is not supported.')

            endpoint.adapter_type = None
            endpoint.mode = None

    def __get_short_type(self, endpoint: ServiceEndpoint) -> str:
        def filter_by_type(cls: SERVICE_CLIENT_CLASS) -> bool:
            if endpoint.model_version == 1.0:
                return endpoint.adapter_type == cls.get_adapter_type()
            elif endpoint.model_version == 2.0:
                return endpoint.type in cls.get_supported_service_types()
            else:
                raise RuntimeError(f'The endpoint {endpoint.id} with model version {endpoint.model_version} is not '
                                   f'supported. Please check your configuration or contact technical support.')

        return SimpleStream(ALL_SERVICE_CLIENT_CLASSES) \
            .filter(filter_by_type) \
            .map(lambda c: c.get_adapter_type()) \
            .find_first()


class EndpointNotFound(RuntimeError):
    def __init__(self, msg: str):
        super().__init__(msg)


class EndpointAlreadyExists(RuntimeError):
    def __init__(self, msg: str):
        super().__init__(msg)


class InvalidConfigurationProperty(RuntimeError):
    def __init__(self, msg: str):
        super().__init__(msg)
