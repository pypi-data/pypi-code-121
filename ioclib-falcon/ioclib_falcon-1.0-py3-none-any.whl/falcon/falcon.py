from typing import Any, Optional, Tuple, Dict
from falcon import Request
from ioclib.injector import Requirement


def header():
    return Requirement(None, None, 'falcon/header')


def parameter():
    return Requirement(None, None, 'falcon/parameter')


def get_falcon_injection(requirement: Requirement, args: Tuple[Any, ...], kwargs: Dict[str, Any]):
    if not requirement.location.startswith('falcon'):
        raise LookupError()

    request = _get_rquest(args)

    if not request:
        raise ValueError()

    if requirement.location == 'falcon/parameter':
        if issubclass(requirement.cls, str):
            return request.get_param(requirement.name, False)

        if issubclass(requirement.cls, int):
            return request.get_param_as_int(requirement.name, False)

        if issubclass(requirement.cls, float):
            return request.get_param_as_float(requirement.name, False)

        if issubclass(requirement.cls, list):
            return request.get_param_as_list(requirement.name, False)

        if issubclass(requirement.cls, dict):
            return request.get_param_as_json(requirement.name, False)

        raise ValueError()

    if requirement.location == 'falcon/header':
        raise NotImplementedError()


def _get_rquest(args: Tuple[Any, ...]) -> Optional[Request]:
    for arg in args:
        if isinstance(arg, Request):
            return arg
