
from .base import Command


class QMCHGCR(Command):
    REQUEST_FMT = 'QMCHGCR'
    RESPONSE_FMT = '{battery_max_charging_current__choices:d}...'
