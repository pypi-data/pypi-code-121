import logging

from typing import Any

from dnastack.common.logger import get_logger

_logger = get_logger('json_path', logging.ERROR)


class BrokenPropertyPathError(AttributeError):
    """ Raised when JsonPath can't retrieve the value at the given property path """
    def __init__(self, obj, path: str, visited_path: str, reason: str, parent = None):
        self.__obj = obj
        self.__path = path
        self.__visited_path = visited_path
        self.__reason = reason
        self.__parent = parent

        super().__init__()

    @property
    def obj(self):
        return self.__obj

    @property
    def visited_path(self):
        return self.__visited_path

    @property
    def reason(self):
        return self.__reason

    @property
    def parent(self):
        return self.__parent

    def __str__(self):
        return f'{type(self.__obj).__name__}: {self.__visited_path}: {self.__reason}'

    def __repr__(self):
        return self.__str__()


class JsonPath:
    @staticmethod
    def set(obj, path: str, value: Any):
        target_property_names = path.split(r'.')
        pointer = JsonPath.get(obj, '.'.join(target_property_names[:-1]), raise_error_on_null=True)
        visited_property_name = target_property_names[-1]

        _logger.debug(f'setter: pointer => {type(pointer)}')
        _logger.debug(f'setter: type(pointer) => {type(pointer)}')
        _logger.debug(f'setter: visited_property_name => {visited_property_name}')

        if hasattr(pointer, visited_property_name):
            setattr(pointer, visited_property_name, value)
        else:
            pointer[visited_property_name] = value

    @staticmethod
    def get(obj, path: str, raise_error_on_null=False) -> Any:
        if not path:
            return obj

        visited_property_names = []
        target_property_names = path.split(r'.')

        parent = None
        node = obj

        while len(target_property_names) > 0:
            target_propert_name = target_property_names.pop(0)
            visited_property_names.append(target_propert_name)

            _logger.debug(f'getter: P/{path}: node => ({type(node)}) {node}')
            _logger.debug(f'getter: P/{path}: target_propert_name => {target_propert_name}')

            if hasattr(node, target_propert_name):
                parent = node
                node = getattr(node, target_propert_name)
            elif isinstance(node, dict):
                parent = node
                node = node.get(target_propert_name)
            else:
                raise BrokenPropertyPathError(
                    obj,
                    path,
                    '.'.join(visited_property_names),
                    'The configuration does not have the specific property.',
                    parent
                )

        if node is None and raise_error_on_null:
            raise BrokenPropertyPathError(
                obj,
                path,
                '.'.join(visited_property_names),
                'Null value',
                parent
            )

        return node
