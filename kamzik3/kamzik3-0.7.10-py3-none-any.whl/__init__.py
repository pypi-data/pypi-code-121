from typing import Optional, TYPE_CHECKING

import oyaml as yaml
from PyQt5.QtCore import QLocale
from oyaml import MappingNode
from pint import UnitRegistry
from pint.quantity import build_quantity_class
import logging


QLocale.setDefault(QLocale("US"))


# TODO: Make save positions group resizable
# TODO: Offer tooltip for saved comment so long comment can be seen
# TODO: Add process ID for session device
# TODO: Somehow make sure, that not two instances of session are running


class GuiTypeError(Exception):
    pass


class WriteException(Exception):
    pass


class DeviceError(Exception):
    pass


class DeviceUnitError(DeviceError):
    pass


class CommandFormatException(DeviceError):
    pass


class DeviceServerError(DeviceError):
    pass


class DeviceClientError(DeviceError):
    pass


class DeviceUnknownError(DeviceError):
    pass


class MacroException(DeviceError):
    pass


class StepSetpointException(MacroException):
    pass


class StepTimeoutException(MacroException):
    pass


def device_constructor(loader, suffix, node):
    arguments = loader.construct_mapping(node, deep=True)
    mapping_node = MappingNode("tag:yaml.org,2002:python/object{}".format(suffix), [])
    new_device = loader.construct_object(mapping_node)
    new_device.__init__(**arguments)
    return new_device


yaml.add_multi_constructor("!Device", device_constructor, Loader=yaml.Loader)
yaml.add_multi_constructor("!Widget", device_constructor, Loader=yaml.Loader)

# Logging setup
SEP = "@!"  # Separator character

"""
Section of units setup, helper functions, ...
"""
units = UnitRegistry()
units.derived_units = []  # type: ignore
q_class = build_quantity_class(units)

if TYPE_CHECKING:
    from kamzik3.devices.deviceSession import DeviceSession

session: Optional["DeviceSession"] = None


def pint_constructor(loader, node):
    value = loader.construct_scalar(node)
    return units.Quantity(value)


def pint_dumper(dumper, data):
    return dumper.represent_scalar("!Pint", str(data))


yaml.add_representer(units.Quantity, pint_dumper)
yaml.add_constructor("!Pint", pint_constructor)

logging.MACRO_STATE = 51  # type: ignore
logging.addLevelName(logging.MACRO_STATE, "MACRO_STATE")  # type: ignore
