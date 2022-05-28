import importlib
import pathlib
from typing import Any, Dict, Optional, Tuple, Union

import reil
from ruamel.yaml import YAML

Parsable = Union[Dict[str, Any], Any]


def from_yaml_file(
        node_reference: Tuple[str, ...],
        filename: str,
        path: Optional[Union[pathlib.PurePath, str]] = None):
    '''
    Create an instance based on a yaml file.

    Arguments
    ---------
    node_reference:
        A list of node names that determines the location of the
        specification in the yaml tree.

    filename:
        Name of the pickle file.

    path:
        Path of the pickle file.

    Returns
    -------
    :
        The generated instance.
    '''
    _path = pathlib.Path(path or '.')
    _filename = filename if filename.endswith((
        '.yaml', '.yml')) else f'{filename}.yaml'

    yaml = YAML()
    with open(_path / _filename, 'r') as f:
        yaml_output: Dict[str, Any] = yaml.load(f)  # type: ignore

    temp_yaml = yaml_output
    for key in node_reference:
        temp_yaml = temp_yaml[key]

    return parse_yaml(temp_yaml)


def parse_yaml(data: Parsable) -> Parsable:  # noqa: C901
    '''
    Parse a yaml tree.

    This method reads a yaml tree and recursively creates objects specified
    by it.

    Arguments
    ---------
    data:
        A yaml tree data.

    Returns
    -------
    :
        Based on the tree, the method returns:

        * A python object, e.g. `int`, `float`, `str`.
        * A dictionary of arguments and their values to be fed to the
            'parse_yaml` caller.
        * An instance of an object derived from `ReilBase`.
    '''
    if isinstance(data, (int, float)):
        return data

    if isinstance(data, str):
        if data.startswith('lambda'):
            return eval(data, {})
        if data.startswith('eval'):
            return eval(data[4:], {})
        return data

    if 'eval' in data:
        args = {'reil': reil}
        if 'args' in data:
            args.update(parse_yaml(data['args']))
        return eval(data['eval'], args)

    if len(data) == 1:
        k, v = next(iter(data.items()))
        result = create_component_from_yaml(k, v)
        if result is not None:
            return result

    args: Dict[str, Any] = {}
    for k, v in data.items():
        if isinstance(v, dict):
            args[k] = parse_yaml(v)  # type: ignore
        elif isinstance(v, list):
            args[k] = [parse_yaml(v_i) for v_i in v]  # type: ignore
        elif isinstance(v, str):
            args[k] = parse_yaml(v)
        else:
            args[k] = v

    return args


def create_component_from_yaml(name: str, args: Dict[str, Any]):
    '''
    Create a component from yaml data.

    This method attempts to import the `reil` class specified in `name`,
    parse arguments specified in `args` and create an instance of the
    class using the parsed arguments. If such class does not exist,
    `None` will be returned.

    Arguments
    ---------
    name:
        Name of the object to be created.

    args:
        A yaml tree section that contains arguments and values to create
        the object.

    Returns
    -------
    :
        The created object or `None`.
    '''
    temp = name.split('.')
    try:
        module = importlib.import_module('.'.join(temp[:-1]))
    except ValueError:
        return None

    f = getattr(module, temp[-1])
    if hasattr(f, 'parse_yaml'):
        result = f(**f.parse_yaml(args))
    else:
        result = f(**parse_yaml(args))

    return result
