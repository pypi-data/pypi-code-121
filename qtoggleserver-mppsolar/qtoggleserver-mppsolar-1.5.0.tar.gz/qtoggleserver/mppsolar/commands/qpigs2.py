
from .base import Command


class QPIGS2(Command):
    REQUEST_FMT = 'QPIGS2'


class QPIGS2_MAX(QPIGS2):
    RESPONSE_FMT = (
        '{pv2_current:f} '
        '{pv2_voltage:f} '
        '{pv2_power:f}'
    )

    UNITS = {
        'pv2_current': 'A',
        'pv2_voltage': 'V',
        'pv2_power': 'W'
    }

    DISPLAY_NAMES = {
        'pv2_current': 'PV2 Current',
        'pv2_voltage': 'PV2 Voltage',
        'pv2_power': 'PV2 Power'
    }
