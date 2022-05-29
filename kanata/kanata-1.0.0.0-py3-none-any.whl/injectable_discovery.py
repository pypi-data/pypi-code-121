"""Utilities for discovering injectables."""

from .constants import LOGGER_NAME
from .models import InjectableRegistration
from types import ModuleType
from typing import Any, List, Optional, Tuple

import importlib
import inspect
import pkgutil
import structlog

def find_injectables(module_name: str) -> Tuple[InjectableRegistration, ...]:
    """Recursively discovers all injectables starting from the specified module.

    :param module_name: The name of the root module.
    :type module_name: str
    :return: The registration objects of the discovered injectables.
    :rtype: Tuple[InjectableRegistration, ...]
    """

    logger = structlog.get_logger(LOGGER_NAME)
    registrations: List[InjectableRegistration] = []
    module_names: List[str] = [module_name]
    while len(module_names) > 0:
        module_name = module_names.pop()
        logger.debug("Loading module", name=module_name)
        module = importlib.import_module(module_name)
        registrations.extend(__get_registrations(module, logger))

        if (path := getattr(module, "__path__", None)) is None:
            continue

        logger.debug("Walking path", path=path)
        for _, name, is_package in pkgutil.walk_packages(path):
            if not is_package:
                continue
            logger.debug("Found additional package", name=name, parent=module_name)
            module_names.append(f"{module_name}.{name}")

    return tuple(registrations)

def __get_registrations(module: ModuleType, logger: Any) -> Tuple[InjectableRegistration, ...]:
    registrations: List[InjectableRegistration] = []
    for _, obj in inspect.getmembers(module, inspect.isclass):
        local_registration: Optional[InjectableRegistration] = getattr(
            obj,
            InjectableRegistration.PROPERTY_NAME,
            None
        )
        if local_registration:
            logger.debug("Found injectable", type=local_registration.injectable_type)
            registrations.append(local_registration)

    return tuple(registrations)
