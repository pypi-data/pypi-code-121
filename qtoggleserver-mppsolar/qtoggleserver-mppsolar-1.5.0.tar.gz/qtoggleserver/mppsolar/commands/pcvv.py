
from .base import Command


class PCVV(Command):
    REQUEST_FMT = 'PCVV{battery_bulk_charging_voltage:04.1f}'
