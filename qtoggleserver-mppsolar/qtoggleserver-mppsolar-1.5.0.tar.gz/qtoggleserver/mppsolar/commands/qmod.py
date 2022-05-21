
from .base import Command

from qtoggleserver.mppsolar import constants


class QMOD(Command):
    REQUEST_FMT = 'QMOD'
    RESPONSE_FMT = '{mode:s}'

    DISPLAY_NAMES = {
        'mode': 'Inverter Mode'
    }

    CHOICES = {
        'mode': constants.MODE_CHOICES
    }
