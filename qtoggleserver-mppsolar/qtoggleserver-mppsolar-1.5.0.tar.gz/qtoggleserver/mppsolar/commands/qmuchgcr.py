
from .base import Command


class QMUCHGCR(Command):
    REQUEST_FMT = 'QMUCHGCR'
    RESPONSE_FMT = '{battery_max_grid_charging_current__choices:d}...'
