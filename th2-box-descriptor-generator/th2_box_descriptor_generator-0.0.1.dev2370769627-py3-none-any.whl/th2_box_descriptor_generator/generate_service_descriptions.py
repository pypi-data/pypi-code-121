import base64
import importlib
import json
from pathlib import Path
import pkg_resources


def get_grpc_modules_names():
    installed_packages = pkg_resources.working_set

    return [package.key.replace('-', '_') for package in installed_packages
            if package.key.startswith('th2-grpc')]


def get_paths_to_package_protos(module_name):
    package = importlib.import_module(module_name, __name__)
    package_path = Path(package.__file__).parent

    return list(package_path.glob('*.proto'))


def create_protos_dict(module_name):
    full_protos_paths = get_paths_to_package_protos(module_name)

    protos_dict = {}
    for proto_path in full_protos_paths:
        relative_proto_path = str(Path(module_name) / proto_path.name)
        with open(proto_path, 'r') as proto_file:
            protos_dict[relative_proto_path] = proto_file.read()

    return protos_dict


if __name__ == '__main__':
    output_filepath = Path('service_proto_description')

    grpc_modules_names = get_grpc_modules_names()
    modules_protos_dict = {grpc_module_name: create_protos_dict(grpc_module_name)
                           for grpc_module_name in grpc_modules_names}

    json_string = json.dumps(modules_protos_dict)
    json_string_base64 = base64.b64encode(json_string.encode('utf-8'))

    with open(output_filepath, 'wb') as output_file:
        output_file.write(json_string_base64)
