"""Scripts generates automatically TrustedTwin client library in Python."""
import argparse
import os
from dataclasses import dataclass
from typing import List, Dict, Tuple
import textwrap
import requests
import yaml
from prance.util.formats import parse_spec, parse_spec_details
from prance.util.resolver import RefResolver

from templates import ACCESS_METHOD_TEMPLATE, ACCESS_CLASS_HEAD_TEMPLATE, ACCESS_FILE_HEAD_TEMPLATE, \
    CLIENT_FILE_HEADER_TEMPLATE, CLIENT_CLASS_HEAD_TEMPLATE, CLIENT_METHOD_TEMPLATE

SWAGGER_SOURCE_URL = 'https://api.swaggerhub.com/apis/{owner}/{api}/{version}/swagger.yaml?resolved=true'
GENERATOR_CONFIG = '{}/api_generator/config.yaml'.format(os.environ['PWD'])
TARGET_DIR_ROOT = '{}/trustedtwin'.format(os.environ['PWD'])
SERVICE_FILE = 'service.py'


def download_swagger_file(version: str) -> str:
    """Download official TrustedTwin swagger."""
    swagger_source_file = SWAGGER_SOURCE_URL.format(
        owner='TrustedTwinDev',
        api='trusted-twin_api',
        version=version
    )
    response = requests.get(swagger_source_file)
    if response.status_code != 200:
        raise ValueError('Could not download OpenAPI definition for version = [{}]'.format(version))
    return response.text


def get_config(path: str) -> Dict:
    """Return bare config as defined in file"""
    with open(path) as fil:
        return yaml.safe_load(fil)


@dataclass
class RESTDefinition:
    """All parameters required to define method"""
    path_params: Dict
    path_params_with_defaults: Dict
    query_params: Dict
    query_params_with_defaults: Dict
    body_required: bool
    method_name: str = ''
    rest_method: str = ''
    endpoint: str = ''
    operation_name: str = ''


class MethodDefinition:
    """Definition of single method that is added to the class"""

    def __init__(self, operation: RESTDefinition):
        self.operation = operation

    def _get_method_arguments(self) -> Tuple[List[str], List[str]]:
        """Return path params and query params in format 'param': 'type'"""
        # arguments and query params returned in format "param_name: type"
        path_params = ['{}: {}'.format(x, y) for x, y in self.operation.path_params.items()]
        if self.operation.path_params_with_defaults:
            path_params.extend(['{}: {}'.format(x, y) for x, y in self.operation.path_params_with_defaults.items()])
        query_params = ['{}: {}'.format(x, y) for x, y in self.operation.query_params.items()]
        if self.operation.query_params_with_defaults:
            query_params.extend(['{}: {}'.format(x, y) for x, y in self.operation.query_params_with_defaults.items()])

        return path_params, query_params

    def _get_endpoint_path(self) -> str:
        """Return definition of an endpoint with arguments formatting"""
        endpoint = "'{}'".format(self.operation.endpoint.strip('/'))

        if self.operation.path_params:
            args = ', '.join(['{}={}'.format(x, x) for x in self.operation.path_params.keys()])
            if self.operation.path_params_with_defaults:
                args += ', ' + ', '.join(['{}={}'.format(x, x) for x in self.operation.path_params_with_defaults.keys()])
            endpoint += '.format({args})'.format(args=args)

        return endpoint

    def render(self) -> str:
        """Render class method definition"""
        path_params, query_params = self._get_method_arguments()

        arguments_line = 'self'
        params_line = ''      # dict of parameters passed in 'params' to http client
        params_filter_line = ''
        has_body = False

        if self.operation.rest_method.upper() in ['POST', 'PATCH', 'PUT']:
            has_body = True

        if has_body and self.operation.body_required:
            arguments_line += ', body: Dict'
        if path_params:
            arguments_line += ', ' + ','.join(path_params)
        if has_body and not self.operation.body_required:
            arguments_line += ', body: Optional[Dict] = None'

        if query_params:
            arguments_line += ', ' + ','.join(query_params)
            all_params = {x for x in self.operation.query_params}
            all_params.update(self.operation.query_params_with_defaults)
            params_line = 'params = {' + ', '.join(['"{}": {}'.format(x, x) for x in all_params]) + '}'
            params_filter_line = 'params = {k: v for k, v in params.items() if v is not None}\n'    # must compare to None!

        code = ACCESS_METHOD_TEMPLATE.format(
            MethodMame=self.operation.method_name,
            Arguments=arguments_line,
            RESTMethod=self.operation.rest_method.upper(),
            Endpoint=self._get_endpoint_path(),
            OperationName=self.operation.operation_name,
            ParamsLine=params_line,
            ParamsFilterLine=params_filter_line,
            PassParams=', params=params' if params_line else '',
            PassBody=', body=body' if has_body else ''
        )

        return code


class AccessClassDefinitions:
    """Definition of a Class"""

    def __init__(self, section: str):
        self.section = section
        self.methods: List[MethodDefinition] = []
        self.import_types = []

    def render_head(self) -> str:
        """Generate code for """
        return ACCESS_CLASS_HEAD_TEMPLATE.format(Section=self.section.capitalize())

    def render_all(self) -> str:
        """Render whole class definition"""
        class_def = self.render_head()
        for method in self.methods:
            class_def += method.render()
        return textwrap.dedent(class_def)


class OperationsFileDefinition:
    """Definition a whole file containing operations class"""

    def __init__(self, class_def: AccessClassDefinitions):
        self.class_def = class_def

    def render(self) -> str:
        """Render whole file including headers section i.e. imports"""
        if self.class_def.import_types:
            import_types = ', {}'.format(', '.join(x for x in set(self.class_def.import_types))).rstrip(',')
        else:
            import_types = ''

        code = ACCESS_FILE_HEAD_TEMPLATE.format(Section=self.class_def.section.capitalize(), ImportTypes=import_types)
        code = textwrap.dedent(code.strip('\n'))
        code += self.class_def.render_all()
        return code


def swagger2python_type(attr_name: str, schema: Dict, class_def: AccessClassDefinitions) -> str:
    """Map Swagger type to python"""
    base_types = {
        'string': 'str',
        'number': 'float',
        'integer': 'int',
        'boolean': 'bool'

    }
    complex_types = {
        'array': 'List'
    }

    if schema['type'] in base_types:
        return base_types[schema['type']]

    typing_type = complex_types[schema['type']]
    class_def.import_types.append(typing_type)

    return '{}[{}]'.format(typing_type, swagger2python_type(attr_name, schema['items'], class_def))


def get_classes_heads_definitions(config: Dict) -> List[AccessClassDefinitions]:
    """Return Class head (init)"""
    return [AccessClassDefinitions(section=sec) for sec in config]


def get_methods_definitions(
        class_def: AccessClassDefinitions,
        config: Dict,
        swagger_data: Dict
) -> List[MethodDefinition]:
    """Return MethodDefinition object for each method within AccessClass"""
    rest_operations = []
    section = class_def.section
    for endpoint_root in swagger_data['paths']:
        for rest_method in swagger_data['paths'][endpoint_root]:
            operation_id = swagger_data['paths'][endpoint_root][rest_method]['operationId']
            if operation_id in config[section]:
                parameters = swagger_data['paths'][endpoint_root][rest_method].get('parameters', {})
                path_params = {}
                path_params_with_defaults = {}
                query_params = {}
                query_params_with_defaults = {}
                body_required = False

                request_body = swagger_data['paths'][endpoint_root][rest_method].get('requestBody')
                if request_body:
                    body_required = request_body.get('required', False)
                    if not body_required:
                        class_def.import_types.append('Optional')

                for param in parameters:
                    if param['in'] == 'query':
                        type_hint = swagger2python_type(param['name'], param['schema'], class_def)
                        if param.get('required', False):
                            query_params[param['name']] = type_hint
                        else:
                            type_hint = 'Optional[{}] = None'.format(type_hint)
                            class_def.import_types.append('Optional')
                            query_params_with_defaults[param['name']] = type_hint

                    if param['in'] == 'path':
                        type_hint = swagger2python_type(param['name'], param['schema'], class_def)
                        if not param['schema'].get('default'):
                            path_params[param['name']] = type_hint
                        else:
                            type_hint = "{} = '{}'".format(type_hint, param['schema']['default'])
                            path_params_with_defaults[param['name']] = type_hint

                method_name = config[section][operation_id]['method_name']
                rest_operations.append(
                    RESTDefinition(
                        path_params=path_params,
                        path_params_with_defaults=path_params_with_defaults,
                        query_params=query_params,
                        query_params_with_defaults=query_params_with_defaults,
                        method_name=method_name,
                        rest_method=rest_method,
                        endpoint=endpoint_root,
                        operation_name=operation_id,
                        body_required=body_required
                    )
                )
    return [MethodDefinition(x) for x in rest_operations]


def generate_client_class(list_of_sections: List[str]):
    """Generate service.py file which contains RestService class"""
    imports_line = '\n'.join(
        ['from trustedtwin.operations.{} import {}Operations'.format(x, x.capitalize()) for x in list_of_sections]
    )
    _fil_code = CLIENT_FILE_HEADER_TEMPLATE.format(OperationsImports=imports_line)
    _fil_code += CLIENT_CLASS_HEAD_TEMPLATE
    for section in list_of_sections:
        _fil_code += CLIENT_METHOD_TEMPLATE.format(
            Section=section,
            SectionCap=section.capitalize()
        )
    with open('{}/{}'.format(TARGET_DIR_ROOT, SERVICE_FILE), 'w+') as fil:
        fil.write(textwrap.dedent(_fil_code))


if __name__ == '__main__':
    args_parser = argparse.ArgumentParser(description='Generator of TrustedTwin API client')
    args_parser.add_argument('-v', '--version', type=str, help='version for which build new client')
    args_parser.add_argument('-p', type=str, help='path to local swagger file')
    args = args_parser.parse_args()
    if args.p:
        fil_path = os.path.realpath('{}/{}'.format(os.curdir, args.p))
        with open(fil_path, 'r') as fil:
            swagger_fil = fil.read()
        resolver = RefResolver(parse_spec_details(swagger_fil)[0], url=fil_path)
        resolver.resolve_references()
        swagger_data = resolver.specs
    else:
        swagger_data = yaml.safe_load(download_swagger_file('2.01.02'))

    cfg_fil = get_config(GENERATOR_CONFIG)
    classes_defs = get_classes_heads_definitions(cfg_fil)

    for class_defs in classes_defs:
        for method in get_methods_definitions(class_defs, cfg_fil, swagger_data):
            class_defs.methods.append(method)

    for class_defs in classes_defs:
        fil_def = OperationsFileDefinition(class_defs)
        os.makedirs('{}/operations'.format(TARGET_DIR_ROOT), exist_ok=True)
        with open('{}/operations/{}.py'.format(TARGET_DIR_ROOT, class_defs.section), 'w+') as fil:
            fil.write(fil_def.render())

    generate_client_class([x.section for x in classes_defs])
