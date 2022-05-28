""" Auto-discover compatible thermometers

This module searches all serial ports on your system and auto-detects
compatible thermometers.

>>> import tc2100.discover.discover
>>> ports = tc2100.discover.discover()
"""

from typing import List, Iterable
from serial.tools.list_ports import comports


VENDOR_ID = (0x10c4, )
""" USB Vendor IDs for the TC2100 """


PRODUCT_ID = (0xea60, )
""" USB Product IDs for the TC2100
"""


def discover(ports: Iterable = None) -> List:
    """ Find all attached digital thermometers

    For this method to work, the USB vendor ID and product ID must be listed
    in `VENDOR_ID` and `PRODUCT_ID`, respectively.

    :param: ports:   List of serial ports, from pyserial. Omit to autoscan.
    :return: List of discovered thermometers. If none are found, returns an
             empty list.
    """
    if ports is None:
        ports = comports(include_links=True)

    return list(filter(_is_tc2100, ports))


def _is_tc2100(port) -> bool:
    try:
        if port.vid not in VENDOR_ID or port.pid not in PRODUCT_ID:
            return False
    except AttributeError:
        return False
    return True
