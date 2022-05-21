from importlib_metadata import version  # type: ignore

from pyswidget.discovery import SwidgetProtocol
from pyswidget.swidgetdimmer import SwidgetDimmer
from pyswidget.device import DeviceType, SwidgetDevice
from pyswidget.exceptions import SwidgetException
from pyswidget.swidgetoutlet import SwidgetOutlet
from pyswidget.swidgetswitch import SwidgetSwitch

__version__ = version("pyswidget")


__all__ = [
    "SwidgetProtocol",
    "DeviceType",
    "SwidgetDevice",
    "SwidgetException",
    "SwidgetDimmer",
    "SwidgetOutlet",
    "SwidgetSwitch",
]
