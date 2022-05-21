
from .base import Command


class PBFT(Command):
    REQUEST_FMT = 'PBFT{battery_float_charging_voltage:04.1f}'
